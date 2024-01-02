# Thermomix 2000

SmartHome web server and controller for local central heating systems.

For now handles visualization of measurements from CH341 MODBUS RTU temperature sensors. 


## Usage

Use microcomputer with connection to MODBUS with sensors.
Debian Bookworm with Python 3.11 tested.

1. Load drivers: `modprobe ch341`.
2. Connect RS485-to-USB converter and find its port. Default: `/dev/ttyUSB0`.
3. Install nginx and copy nginx.conf to `/etc/nginx/sites-available/default`.
4. Install requirements.txt using pip and gunicorn using apt.
5. Copy application to `/srv/thermomix`.
6. Provide htpasswd file in `/etc/nginx/` to have basic auth features.
7. Use config_template.py to create config.py with map of devices.
8. Provide dashboard.jpg file in `static` directory with central heating system schema.
9. Serve application (possibly as a daemon) using `gunicorn -k uvicorn.workers.UvicornWorker thermomix.serve:app``
