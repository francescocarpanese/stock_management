
from stock_management.formatting_utils import normalize_text, process_file


input_file = '/Users/francescocarpanese/Documents/stock_management/test_data/drug_list_raw.txt'
output_file = '/Users/francescocarpanese/Documents/stock_management/assets/drug_list.txt'

process_file(input_file, output_file)