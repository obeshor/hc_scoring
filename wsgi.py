from hc_scoring_api import app as appb
from hc_scoring_dash import app as appf
from multiprocessing import Process

if __name__ == "__main__":
    p1 = Process(target=appb.run(debug=True))
    p1.start()
    p2 = Process(target=appf.run_server(debug=True))
    p2.start()
    p1.join()
    p2.join()
    #appb.run(debug=True)
    #appf.run(debug=True)
