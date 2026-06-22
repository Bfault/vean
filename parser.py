import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import orjson
from tqdm import tqdm

from config import load_config
from enricher import enrich_entry
from extractor import get_dynamic_modules, load_progress, run_extraction_batch, save_progress


def process_batch(batch, config):
    entries = []
    try:
        for raw in run_extraction_batch(batch, config):
            if "name" in raw:
                entries.append(enrich_entry(raw, config))
    except Exception as e:
        print(f"Erreur lot: {e}")
    return batch, entries


def run_pipeline():
    config = load_config()
    start_time = time.time()
    total_extracted = 0

    modules = get_dynamic_modules(config)
    processed = load_progress(config.output.progress_file)
    modules = [m for m in modules if m not in processed]
    print(f"Reprise: {len(processed)} modules déjà traités, {len(modules)} restants")
    batch_size = config.extraction.batch_size
    max_workers = config.extraction.max_workers

    print(f"Extracting {len(modules)} files (in batches of {batch_size})...\n")

    with open(config.output.dataset_file, 'wb') as f_out:
        with tqdm(total=len(modules), desc="Global Progress", position=0, leave=True, colour="green") as main_pbar:
            if max_workers > 1:
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = {}
                    for i in range(0, len(modules), batch_size):
                        batch = modules[i:i + batch_size]
                        future = executor.submit(process_batch, batch, config)
                        futures[future] = batch

                    for future in as_completed(futures):
                        batch, entries = future.result()
                        for entry in entries:
                            total_extracted += 1
                            f_out.write(orjson.dumps(entry) + b'\n')
                        processed.update(batch)
                        save_progress(config.output.progress_file, processed)
                        main_pbar.update(len(batch))
            else:
                for i in range(0, len(modules), batch_size):
                    batch = modules[i:i + batch_size]
                    main_pbar.set_description(f"Lot {i//batch_size + 1}/{(len(modules)//batch_size) + 1}")

                    exact_total = None
                    module_pbar = None
                    try:
                        for raw in run_extraction_batch(batch, config):
                            if "total_theorems" in raw:
                                exact_total = raw["total_theorems"]
                                if exact_total > 0:
                                    module_pbar = tqdm(
                                        total=exact_total,
                                        desc="↳ Theorems",
                                        position=1,
                                        leave=False,
                                        colour="blue",
                                    )
                                continue

                            if "name" in raw:
                                total_extracted += 1
                                entry = enrich_entry(raw, config)
                                f_out.write(orjson.dumps(entry) + b'\n')
                                if module_pbar:
                                    module_pbar.update(1)
                    except Exception as e:
                        print(f"Erreur sur le lot {i//batch_size + 1}: {e}")
                    finally:
                        if module_pbar:
                            module_pbar.close()
                        processed.update(batch)
                        save_progress(config.output.progress_file, processed)
                        main_pbar.update(len(batch))

    elapsed = time.time() - start_time
    print(f"\nPipeline completed! {total_extracted} theorems extracted in {elapsed:.2f} seconds.")


if __name__ == "__main__":
    run_pipeline()
