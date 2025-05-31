# MF Seasonality Analysis Tool

## Overview
The MF Seasonality Analysis Tool is a Streamlit application designed to visualize the seasonality of mutual fund schemes. It allows users to select one or more mutual fund schemes and generates visualizations that highlight the average monthly returns and seasonal trends.

## Features
- Search and select mutual fund schemes.
- Visualize seasonality through heatmaps and bar plots.
- Download visualizations as a PDF.

## Installation
To run this application, you need to have Python installed on your machine. Follow these steps to set up the project:

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/MF-Seasonality-Analysis-Tool.git
   ```
   
2. Navigate to the project directory:
   ```
   cd MF-Seasonality-Analysis-Tool
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage
To run the Streamlit application, execute the following command in your terminal:
```
streamlit run app.py
```

Open your web browser and go to `http://localhost:8501` to access the application.

## Dependencies
The application requires the following Python packages:
- Streamlit
- pandas
- numpy
- matplotlib
- seaborn
- mftool

These dependencies are listed in the `requirements.txt` file.

## Contributing
Contributions are welcome! If you have suggestions for improvements or new features, please open an issue or submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
This application utilizes the mftool library for fetching mutual fund data and relies on various data visualization libraries for presenting the analysis.