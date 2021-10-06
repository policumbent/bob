from flask import Flask
import systemd_manager

app = Flask(__name__)
manager = systemd_manager.SystemdManager()


@app.route("/")
def hello_world():
    return "<p>Use the API with /&lt;module-name&gt;/[start/status/stop/restart]</p>"


@app.route('/<module>/start', methods=['POST'])
def start_service(module):
    if not manager.is_active(module):
        manager.start_unit(module)


@app.route('/<module>/stop', methods=['POST'])
def stop_service(module):
    if manager.is_active(module):
        manager.stop_unit(module)


@app.route('/<module>/restart', methods=['POST'])
def restart_service(module):
    if manager.is_active(module):
        if manager.stop_unit(module):
            manager.start_unit(module)


@app.route('/<module>/enable', methods=['POST'])
def enable_service(module):
    manager.enable_unit(module)


@app.route('/<module>/disable', methods=['POST'])
def disable_service(module):
    manager.disable_unit(module)


@app.route('/<module>/status', methods=['GET'])
def service_status(module):
    if manager.is_active(module):
        return '<p>{module} is active</p>'.format(module=module)
    else:
        return '<p>{module} is not active</p>'.format(module=module)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
