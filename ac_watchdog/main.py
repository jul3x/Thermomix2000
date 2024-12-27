from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from enum import Enum
import minimalmodbus
import serial
import time

from ac_watchdog.config import (
    USB_DEVICE,
    IO_REGISTER, 
    IO_BIT,
    INTERVAL, 
    WRONG_STATE, 
    HYSTERESIS_TIMEOUT,
    SMTP_SERVER,
    SMTP_PORT,
    SENDER_EMAIL,
    SENDER_PASSWORD,
    RECIPIENT_EMAIL,
)

class MeasureException(Exception):
    pass

def get_io_state():
    try:
        return _get_io_state()
    except serial.serialutil.SerialException:
        raise MeasureException("MODBUS Connector not found in given port")
    except minimalmodbus.NoResponseError:
        raise MeasureException("One of devices did not respond")


def _get_io_state():
    instrument = minimalmodbus.Instrumenti(USB_DEVICE,
                                          1,
                                          mode=minimalmodbus.MODE_RTU)

    instrument.serial.baudrate = 9600
    instrument.serial.bytesize = 8
    instrument.serial.stopbits = 1
    instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
    instrument.serial.timeout = 1

    instrument.close_port_after_each_call = True
    instrument.clear_buffers_before_each_transaction = True

    io_values = instrument.read_register(IO_REGISTER)
    io_value = bin(io_values)[-IO_BIT]
    return io_value == '1'


class State(str, Enum):
    CORRECT = 'CORRECT'
    INCORRECT = 'INCORRECT'
    COMMUNICATION_ERROR = 'COMMUNICATION_ERROR'


def watch_state():
    current_state_hysteresis = State.CORRECT
    current_state = State.CORRECT
    last_current_state_ts = 0

    notified = False

    while True:
        try:
            io_state = get_io_state()
            current_state = State.INCORRECT if io_state == WRONG_STATE else State.CORRECT
        except MeasureException:
            current_state = State.COMMUNICATION_ERROR

        print(f'Measured state: {current_state}')

        if current_state == current_state_hysteresis:
            last_current_state_ts = time.time()

        if time.time() - last_current_state_ts > HYSTERESIS_TIMEOUT:
            notified = notify(current_state_hysteresis, current_state)

            if notified:
                current_state_hysteresis = current_state

        time.sleep(INTERVAL)


def notify(previous_state, current_state):
    current_time = datetime.now()
    time_string = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f'{time_string}: Notifying because state changed from {previous_state} to {current_state}')
    
    subject = time_string + ": "
    if previous_state == State.CORRECT:
        if current_state == State.INCORRECT:
            state = 'UWAGA! Zanik prądu!'
        if current_state == State.COMMUNICATION_ERROR:
            state = 'UWAGA! Błąd komunikacji z urządzeniem!'
    if previous_state == State.INCORRECT:
        if current_state == State.CORRECT:
            state = 'Prąd powrócił!'
        if current_state == State.COMMUNICATION_ERROR:
            state = 'UWAGA! Nie było prądu i teraz nie ma już komunikacji z urządzeniem!'
    if previous_state == State.COMMUNICATION_ERROR:
        if current_state == State.CORRECT:
            state = 'Komunikacja z urządzeniem odzyskana!'
        if current_state == State.INCORRECT:
            state = 'UWAGA! Komunikacja z urządzeniem odzyskana, nie ma prądu!'

    subject += state
    body = 'Nastąpiła zmiana stanu urządzenia.\n' + \
            f'Czas: {time_string} \n' + \
            f'Status: {state}'
    return send_mail(subject, body)

def send_mail(subject, body):
    server = None
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.starttls()  
        server.login(SENDER_EMAIL, SENDER_PASSWORD)  

        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Error: {e}")
        
    if server:
        server.quit()

    return False


if __name__ == "__main__":
    watch_state()

