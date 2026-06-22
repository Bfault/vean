import time
from tqdm import tqdm
import orjson
from config import load_config
from extractor import get_dynamic_modules, run_extraction_batch
from enricher import enrich_entry


def run_pipeline():
    config = load_config()
    start_time = time.time()
    total_extracted = 0

    modules = get_dynamic_modules(config)
    batch_size = config.extraction.batch_size

    print(f"Extracting {len(modules)} files (in batches of {batch_size})...\n")

    with open(config.output.dataset_file, 'wb') as f_out:
        with tqdm(total=len(modules), desc="Global Progress", position=0, leave=True, colour="green") as main_pbar:
            for i in range(0, len(modules), batch_size):
                batch = modules[i:i + batch_size]
                main_pbar.set_description(f"Lot {i//batch_size + 1}/{(len(modules)//batch_size) + 1}")

                exact_total = None
                module_pbar = None

                for raw in run_extraction_batch(batch, config):
                    if "total_theorems" in raw:
                        exact_total = raw["total_theorems"]
                        if exact_total > 0:
                            module_pbar = tqdm(total=exact_total, desc="↳ Theorems", position=1, leave=False, colour="blue")
                        continue

                    if "name" in raw:
                        total_extracted += 1
                        entry = enrich_entry(raw, config)
                        f_out.write(orjson.dumps(entry) + b'\n')
                        if module_pbar:
                            module_pbar.update(1)

                if module_pbar:
                    module_pbar.close()
                main_pbar.update(len(batch))

    elapsed = time.time() - start_time
    print(f"\nPipeline completed! {total_extracted} theorems extracted in {elapsed:.2f} seconds.")


if __name__ == "__main__":
    run_pipeline()
