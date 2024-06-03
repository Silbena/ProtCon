import converters.csvConverter as csv
# Add the rest of converters

def get_converters() -> list:
    return [
        csv.CsvToTsv,
        csv.TsvToCsv
        ]
