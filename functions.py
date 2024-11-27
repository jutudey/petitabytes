import numpy as np
import streamlit as st
import functions as functions
import config
import pandas as pd
from PIL import Image
import re
import os
import datetime
import zipfile
from io import BytesIO
import zipfile
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,)

def set_page_definitition():
    app_name = config.app_name

    # Loading Image using PIL
    # icon = Image.open('content/Subsidiary Salmon Logo.png')

    # Enable wide mode and set light theme and add tab icon
    st.set_page_config(layout="wide", page_title=app_name, initial_sidebar_state="expanded")
    # st.set_page_config(layout="wide", page_title=app_name, page_icon=":material/sound_detection_dog_barking:", initial_sidebar_state="expanded")

    return app_name