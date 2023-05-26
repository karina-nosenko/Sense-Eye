# CSS styles
buttonStyle = '''padding: 10px;
			font-size: 18px;
			border: none;
			background-color: #333;
			color: #fff;
			border-radius: 4px;'''

headingStyle = '''font-size: 50px;
			font-weight: bold;
            font-family: sans-serif;
			color: #000;'''

labelStyle = '''font-size: 24px;
            font-family: sans-serif;
			color: #505050;'''

inputStyle = """
    QLineEdit {
        background-color: #f2f2f2;
        border: none;
        border-radius: 10px;
        font-size: 16px;
        padding: 10px;
    }
"""

selectorStyle = """
    QComboBox {
                background-color: #F0F0F0;
                color: #000000;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
    }
    
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 20px;
        
        border-left-width: 1px;
        border-left-color: #CCCCCC;
        border-left-style: solid;
        border-top-right-radius: 5px;
        border-bottom-right-radius: 5px;
    }
    
    QComboBox::down-arrow {
        image: url(icons/down_arrow.png);
        background-position: center;
        background-repeat: no-repeat;
        background-size: 5px 5px;
    }
"""

alertStyle = """
    QMessageBox {
        background-color: #f2f2f2;
        border: 1px solid #dddddd;
        border-radius: 4px;
    }
    QLabel {
        color: #333333;
    }
    QPushButton {
        background-color: #007bff;
        color: #ffffff;
        padding: 5px 10px;
        border-radius: 4px;
    }
    QPushButton:hover {
        background-color: #0056b3;
    }
"""