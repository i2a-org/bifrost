
from api.API import API
import os

################################################################################
#
# Call app based on deployment environment;
#
endpoints = API(os.environ["ENV"])
application = endpoints.getApp()
if __name__ == "__main__":
    if os.environ["ENV"] == "dev": application.run(debug=True)
    elif os.environ["ENV"] == "staging": application.run(debug=True)
    elif os.environ["ENV"] == "production": application.run()
