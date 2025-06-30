# Pandera: A Data Validation Toolkit for Data Scientists & Engineers

![Intro](images/pandera.png)

---

## What is Pandera?

Pandera is a powerful and flexible **data validation** library for Python, designed to check dataframe-like objects. Think of it as a quality control checkpoint for your data.

In any data pipeline, from analytics to machine learning, the quality of your output is determined by the quality of your input. Pandera helps you prevent the "**Garbage In, Garbage Out**" problem by allowing you to define a clear, readable, and explicit schema, or "**contract**," for your data. 

This contract specifies rules that your data must follow, such as:

- The data types of columns (int, str, datetime).
- The range of acceptable values (age > 0, score between 0 and 100).
- Unique or required columns.
- More complex statistical properties.


By validating your data against this schema at runtime, Pandera makes your data processing pipelines more readable, robust, and easier to debug.

