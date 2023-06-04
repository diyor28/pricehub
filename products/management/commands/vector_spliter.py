import os
import numpy as np
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Splits a single .npz file into multiple files'

    def add_arguments(self, parser):
        parser.add_argument('input_file', type=str, help='Path to the input .npz file')
        parser.add_argument('num_splits', type=int, help='Number of splits')

    def handle(self, *args, **options):
        input_file = options['input_file']
        num_splits = options['num_splits']

        if not os.path.isfile(input_file):
            self.stdout.write(self.style.ERROR(f"Input file '{input_file}' does not exist."))
            return

        try:
            data = np.load(input_file)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to load input file '{input_file}': {str(e)}"))
            return

        try:
            output_dir = os.path.splitext(input_file)[0]
            os.makedirs(output_dir, exist_ok=True)

            arrays = list(data.keys())
            split_size = data[arrays[0]].shape[0] // num_splits

            for i in range(num_splits):
                start_index = i * split_size
                end_index = (i + 1) * split_size

                split_data = {}
                for array in arrays:
                    split_data[array] = data[array][start_index:end_index]

                output_file = os.path.join(output_dir, f'split_{i+1}.npz')
                np.savez(output_file, **split_data)
                self.stdout.write(self.style.SUCCESS(f"Split {i+1}: {output_file} created."))

            self.stdout.write(self.style.SUCCESS(f"Splitting completed successfully."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Splitting failed: {str(e)}"))
            return
