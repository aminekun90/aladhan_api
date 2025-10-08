# Calendar

A Python library for accurate Hijri-Gregorian date conversion using the Umm al-Qura calendar.

Calendar provides reliable date conversion based on official sources, including archived Umm al-Qura newspaper publications and comparative calendar data from King Abdulaziz City for Science and Technology (KACST). The package has been thoroughly tested and verified against original references to ensure accuracy and reliability.

## ✨ Features

- Accurate and verified Hijri-Gregorian date conversion
- Based on official Umm al-Qura calendar sources and archived publications
- Optimized performance compared to existing implementations
- Comprehensive input validation and error handling
- Multilingual support for Arabic, English, and other languages
- Rich comparison operations and date formatting options
- Full type annotations and 100% test coverage
- Zero runtime dependencies
- Compatible with Python 3.9+

## ⚠️ Limitations

**Date Range**: The converter supports dates from 1343 AH to 1500 AH (1 August 1924 CE to 16 November 2077 CE), corresponding to the period covered by available official calendar sources.

**Religious Context**: Not intended for religious purposes where lunar crescent sighting is preferred over astronomical calculations.

## 🚀 Basic Usage

```python
from calculations.calendar import Hijri, Gregorian

# Convert a Hijri date to Gregorian
hijri_date = Hijri(1445, 6, 15)
gregorian_date = hijri_date.to_gregorian()
print(gregorian_date)  # 2023-12-28

# Convert a Gregorian date to Hijri
gregorian_date = Gregorian(2023, 12, 28)
hijri_date = gregorian_date.to_hijri()
print(hijri_date)  # 1445-06-15
```

<!-- end summary -->

## 📚 Documentation

Please refer to <https://hijridate.readthedocs.io> for complete documentation on this package, which includes background information, benchmarking, usage examples, and API reference.

## 🤝 Contributing

TBD

## 📄 License

This Library is licensed under the terms of the MIT license.

<!-- start attrs -->

## 🙏 Acknowledgements

TBD

## 📝 Citation

TBD
