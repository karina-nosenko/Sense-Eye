from flask import Flask, request
import requests
flaskApp = Flask(__name__)

mapping_color_to_ip = {}
mapping_ip_to_color = {}
current_player_with_the_ball_color_ip = None  # we will have his ip in here


@flaskApp.route('/recommend') # output D1-GPIO5-5 D2-GPIO4-4 D3-GPIO0-0 D4-GPIO2-2
def recommend():
    color = request.args.get('color')
    output_state = request.args.get('output_state')  # output D1-GPIO5-5 D2-GPIO4-4 D3-GPIO0-0 D4-GPIO2-2
    state = request.args.get('state')
    current_player_with_the_ball_ip = mapping_color_to_ip[color]
    print('http://'+current_player_with_the_ball_ip+'/recommend/'+ state + '/' + output_state)
    requests.get('http://'+current_player_with_the_ball_ip+'/recommend/'+ state + '/' + output_state)

    return "Data received"


@flaskApp.route('/save_id')
def save_id():
    color_band = request.args.get('color_band')
    ip = request.args.get('ip')
    mapping_color_to_ip[color_band] = ip
    mapping_ip_to_color[ip] = color_band
    print("ip is = " + ip)
    print("color_band is = " + color_band)

    return "Data received"


@flaskApp.route('/status')
def show_connected_players():
    for key in mapping_color_to_ip:
        print(key)
    return "Data received"


if __name__ == '__main__':
    flaskApp.run(host='0.0.0.0', port=5000, threaded=False)
