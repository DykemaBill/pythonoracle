from sqlalchemy import create_engine # Library to talk with Oracle
import logging, logging.handlers, json, sys
from datetime import datetime
import encryptpass as encryptpass

# Configuration file name
config_name = 'settings'
config_file = config_name + '.cfg'

# Log file name
log_name = 'pythonoracle'
log_file = log_name + '.log'
# Start logger
logger = logging.getLogger('Logger')

# Decryption key for encrypted passwords
decryption_key = '7Ju5JdJAvW6aFEIhFTxTebvfVqkEsn_fbFjoHVbWV9w='

# Set default configuration variables
support_team = "needtosetteamname"
support_email = "needtosetinconfig@nowhere.com"
logfilesize = [ 10000, 9 ] # 10000 is 10k, 9 is 10 total copies

# Database configuration variables
db_connection = "willbesetusingfourpartsbelow"
db_connection_log = "willbeusedintheconsole"
db_conn_type = "dbtype"
db_conn_acct = "youraccount"
db_conn_pass = "yourpassword"
db_conn_pass_encrypted = "yourpasswordencrypted"
db_conn_host = "yourdbhost"
db_conn_database = "yourdatabase"

# Read configuration file function
config_error = False
def config_file_read(config_file_name):
    try:
        with open(config_file_name, 'r') as config_contents:
            cfg_data = json.loads(config_contents.read())
            
            global logfilesize
            global support_team
            global support_email

            global db_connection
            global db_connection_log
            global db_conn_type
            global db_conn_acct
            global db_conn_pass_encrypted
            global db_conn_pass
            global db_conn_host
            global db_conn_database

            # Read log file settings
            logfilesize.clear()
            logfilesize.append(cfg_data['logfilesize'][0])
            logfilesize.append(cfg_data['logfilesize'][1])

            # Read team description
            support_team = cfg_data['team']

            # Read support email address
            support_email = cfg_data['email']

            # Read DB type
            db_conn_type = cfg_data['db_target_type']
            # Read target DB account
            db_conn_acct = cfg_data['db_target_acct']
            # Read target DB encrypted password
            db_conn_pass_encrypted = cfg_data['db_target_pass']
            # Decrypt target DB byte to plain text password
            db_conn_pass = encryptpass.passdecrypt(decryption_key, db_conn_pass_encrypted)
            # Read target DB host name
            db_conn_host = cfg_data['db_target_host']
            # Read target DB name
            db_conn_database = cfg_data['db_target_database']
            # Assemble target string
            db_connection = db_conn_type + "://" + db_conn_acct + ":" + db_conn_pass + "@" + db_conn_host + "/" + db_conn_database
            # Log target  string
            db_connection_log = db_conn_type + "://" + db_conn_acct + ":" + "********" + "@" + db_conn_host + "/" + db_conn_database

    except IOError:
        print('Problem opening ' + config_file + ', check to make sure your configuration file is not missing.')
        global config_error
        config_error = True

# Setup logging
def log_file_setup(log_file_name):
    global config_error
    # Set logger to desired output level
    logger.setLevel(logging.INFO)
    # Setup log handler to manage size and total copies
    handler = logging.handlers.RotatingFileHandler(log_file_name, maxBytes=logfilesize[0], backupCount=logfilesize[1])
    # Setup formatter to prefix each entry with date/time 
    formatter = logging.Formatter("%(asctime)s - %(message)s")
    # Add formatter
    handler.setFormatter(formatter)
    # Add handler
    logger.addHandler(handler)

    # Config file status
    if config_error == True:
        print ("Unable to set config variables")
        logger.info('Problem opening ' + config_file + ', check to make sure your configuration files are not missing.')
    else: # Config settings out to the log
        print ("Configuration files read")
        logger.info('Log file size is set to ' + str(logfilesize[0]) + ' bytes and ' + str(logfilesize[1]) + ' copies')
        logger.info('Email is set to: ' + support_email)
        logger.info('Team is set to: ' + support_team)

# Database connection
def setup_database(db_connection_path):
    # Oracle object, db_target_type of postgres for local host
    if config_error == False:
        db_inst_setup = create_engine(db_connection_path)
    else:
        print('Database not connected because of problem opening ' + config_file + '.')
    return db_inst_setup

# Database test
def test_database(db_inst, db_numfield, db_textfield):
    global config_error
    records_list = []
    if config_error == False:
        # Current hour
        nowHour = int(datetime.now().strftime("%H"))
        print ("Current hour is: " + str(nowHour))
        # Delete table just for testing purposes
        db_inst.execute("DROP TABLE IF EXISTS testtable")
        # Create target relational table if it does not exist already
        db_inst.execute("CREATE TABLE IF NOT EXISTS testtable (test_datetime timestamptz, test_number bigint, test_text text)")  
        # Current date/time
        nowIs = datetime.now().strftime("%Y-%m-%d %H:%M:%S-00")
        # Write to relational database
        db_inst.execute("INSERT INTO testtable (test_datetime, test_number, test_text) VALUES ('" + nowIs + "', " + str(db_numfield) + ", '" + str(db_textfield) + "')")
        print ("Reading table back...")
        records_list = db_inst.execute("SELECT * FROM testtable") 
        for record in records_list:
           print (str(record))
    else:
        print ("Error reading configuration")

# Get command line arguments
if __name__ == "__main__":
    if len(sys.argv) == 3:
        # Read configuration file
        print ("Reading configuration file: " + str(config_file))
        config_file_read(config_file)
        # Log file setup
        print ("Setting up log file: " + str(log_file))
        log_file_setup(log_file)
        # Database connection
        print ("Connecting to database: " + str(db_connection_log))
        db_inst = setup_database(db_connection, sys.argv[1], sys.argv[2])
        # Database test
        print ("Reading from database...")
        test_database(db_inst)
    else:
        print ("Syntax:")
        print ("        " + sys.argv[0] + " [int for 1st field] [text for 2nd field]")