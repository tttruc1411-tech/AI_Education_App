# LLM Worker — Subprocess for GPU inference on Jetson Orin Nano
# Runs in its own process so CUDA CMA is not shared with PyTorch/YOLO.
# Protocol: reads JSON commands from stdin, writes responses to stdout.

import sys
import os
import json


def _get_cma_free_mb():
    """Read CmaFree from /proc/meminfo. Returns MB or 9999 if unavailable."""
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("CmaFree:"):
                    return int(line.split()[1]) // 1024
    except Exception:
        pass
    return 9999


def main():
    # Force unbuffered stdout for streaming tokens
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

    llm = None
    cfg = None
    Llama = None

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            cmd = json.loads(line)
        except json.JSONDecodeError:
            continue

        action = cmd.get("action")

        if action == "load":
            model_path = cmd["model_path"]
            cfg = cmd["config"]
            gpu_layers = cfg.get("gpu_layers", 999)

            # Check if GPU is feasible: need at least ~200 MB CMA free
            # for cudaMalloc to succeed on Jetson Orin Nano.
            cma_free = _get_cma_free_mb()
            use_gpu = gpu_layers > 0 and cma_free > 200

            if not use_gpu:
                # Hide CUDA before importing llama_cpp so ggml_cuda_init
                # never registers the CUDA backend.
                os.environ["CUDA_VISIBLE_DEVICES"] = ""

            try:
                from llama_cpp import Llama as _Llama
                Llama = _Llama

                llm = Llama(
                    model_path=model_path,
                    n_ctx=cfg.get("context_len", 4096),
                    n_gpu_layers=gpu_layers if use_gpu else 0,
                    n_threads=cfg.get("threads", 6),
                    use_mmap=True,
                    use_mlock=False,
                    verbose=False,
                )
                mode = "gpu" if use_gpu else "cpu"
                print(f"STATUS:ready:{mode}", flush=True)
            except Exception as e:
                print(f"STATUS:error:{e}", flush=True)

        elif action == "infer":
            if llm is None:
                print("STATUS:error:model not loaded", flush=True)
                continue
            prompt = cmd["prompt"]
            try:
                stream = llm(
                    prompt,
                    max_tokens=cfg.get("max_tokens", 512),
                    temperature=cfg.get("temperature", 0.2),
                    top_p=cfg.get("top_p", 0.9),
                    repeat_penalty=cfg.get("repeat_penalty", 1.1),
                    stop=cfg.get("stop", []),
                    stream=True,
                )
                for chunk in stream:
                    token = chunk["choices"][0]["text"]
                    print(f"TOKEN:{token}", flush=True)
                print("STATUS:done", flush=True)
            except Exception as e:
                print(f"STATUS:error:{e}", flush=True)

        elif action == "unload":
            if llm is not None:
                del llm
                llm = None
                import gc
                gc.collect()
            print("STATUS:unloaded", flush=True)

        elif action == "quit":
            if llm is not None:
                del llm
            break

    sys.exit(0)


if __name__ == "__main__":
    main()
