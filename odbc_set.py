# Libraries related to getting the appropriate credentials
import requests, json, sys, os
# Library to talk with Oracle, requires Python cx_Oracle module and the Oracle Instant Client to be installed on host
from sqlalchemy import create_engine

# Configuration
passwordstate_url = "https://passwordstate.[yourinstall].com/api/passwords"

# Setup logging
def odbc_setup(db_set):
    db_set = db_set.upper()
    global passwordstate_url
    # Environmental path
    path_from = str(os.getcwd())
    env_set = os.path.basename(path_from)
    # Check development environment folder, set to DEV is not QA or PRD
    if (env_set != "QA" and env_set != "PRD" ):
        env_set = "DEV"
    # Set API password and key
    password_id_get = "DB_USER_RSTUDIO_" + db_set + "_PASSWORDID_" + env_set
    password_id = os.environ.get(password_id_get)
    api_key_get = "DB_USER_RSTUDIO_" + db_set + "_APIKEY_" + env_set
    api_key = os.environ.get(api_key_get)
    # Set Passwordstate request string
    ps_url = passwordstate_url + "/" + str(password_id) + "?apikey=" + str(api_key)
    # Get Passwordstate response
    ps_response = requests.get(ps_url).json()
    # Pull user and password from response
    db_user = ps_response[0]["UserName"]
    db_pass = ps_response[0]["Password"]
    # Set Oracle database DSN name
    dsn_get = "PY_DSN_" + db_set + "_" + env_set
    db_dsn = os.environ.get(dsn_get)
    # Create connection
    db_connection = "oracle+cx_oracle://" + db_user + ":" + db_pass + "@" + db_dsn
    # Database connection cursor
    db_inst = create_engine(db_connection)
    return (db_inst)

# Command line how-to
if __name__ == "__main__":
    if len(sys.argv) == 2:
        # Database being used
        db_set = sys.argv[1]
        # Get the Oracle connection cursor using the area passed and folder name that this is running from
        db_cursor = odbc_setup(db_set)
        print ("Oracle database connection cursor is setup!")
    else:
        print ("Syntax:")
        print ("        " + sys.argv[0] + " [area]")