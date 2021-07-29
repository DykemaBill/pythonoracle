from sqlalchemy import create_engine # Library to talk with Oracle, requires Python cx_oracle module and the Oracle Instant Client to be installed
from sqlalchemy import Column, DateTime, BigInteger, Text # Used to make Oracle easier to query
from sqlalchemy.ext.declarative import declarative_base # Used to make Oracle easier to query
from sqlalchemy.orm import sessionmaker # Used to make Oracle easier to query
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

# Database ORM setup
db_base = declarative_base()
class TestTable(db_base):  
    __tablename__ = 'testtable'
    test_datetime = Column(DateTime, primary_key=True)
    test_number = Column(BigInteger)
    test_text = Column(Text)

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
            db_conn_type = cfg_data['db_conn_type']
            # Read DB account
            db_conn_acct = cfg_data['db_conn_acct']
            # Read DB encrypted password
            db_conn_pass_encrypted = cfg_data['db_conn_pass']
            # Decrypt DB byte to plain text password
            db_conn_pass = encryptpass.passdecrypt(decryption_key, db_conn_pass_encrypted)
            # Read DB host name
            db_conn_host = cfg_data['db_conn_host']
            # Read DB name
            db_conn_service = cfg_data['db_conn_service']
            # Assemble string
            db_connection = db_conn_type + "://" + db_conn_acct + ":" + db_conn_pass + "@" + db_conn_host + "/" + db_conn_service
            # Log string
            db_connection_log = db_conn_type + "://" + db_conn_acct + ":" + "********" + "@" + db_conn_host + "/" + db_conn_service

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
    if config_error == False:
        print ("Connecting to database: " + str(db_connection_log))
        # Database connection
        db_inst_setup = create_engine(db_connection_path)
        # Database wrap connection with ORM class
        DB_Session = sessionmaker(db_inst_setup)  
        db_session_path = DB_Session()
        db_base.metadata.create_all(db_inst_setup)
    else:
        print('Database not connected because of problem opening ' + config_file + '.')
    return db_inst_setup, db_session_path

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
        # Create relational table if it does not exist already
        db_inst.execute("CREATE TABLE IF NOT EXISTS testtable (test_datetime timestamptz, test_number bigint, test_text text)")  
        # Current date/time
        nowIs = datetime.now().strftime("%Y-%m-%d %H:%M:%S-00")
        # Write to relational database
        db_inst.execute("INSERT INTO testtable (test_datetime, test_number, test_text) VALUES ('" + nowIs + "', " + str(db_numfield) + ", '" + str(db_textfield) + "')")
        print ("Reading table back...")
        records_list = db_inst.execute("SELECT * FROM testtable") 
        print ("Records after adding:")
        for record in records_list:
           print (str(record))
    else:
        print ("Error reading configuration")

# Database query test with ORM (Object Relational Mapper)
def test_orm(db_session, db_numfield_filter):
    global config_error
    record_count = 0
    records_list = []
    if config_error == False:
        # Query
        query_run = "and_(TestTable.test_number" + " == " + db_numfield_filter + ")"
        # Record count
        record_count = db_session.query(TestTable).filter(eval(query_run)).count()
        # Get values
        records_list = list(db_session.query(TestTable).filter(eval(query_run)))
        print ("Record count: " + record_count)
        print ("Records querying filtering for '" + db_numfield_filter + "':")
        for record in records_list:
           print (str(record))
    else:
        print ("Error reading configuration")

# Read config, start logging and setup database connection
def startup_here():
    # Read configuration file
    print ("Reading configuration file: " + str(config_file))
    config_file_read(config_file)
    # Log file setup
    print ("Setting up log file: " + str(log_file))
    log_file_setup(log_file)
    # Database connection
    print ("Connecting to database: " + str(db_connection_log))
    logger.info('Connecting to database: ' + str(db_connection_log))
    db_inst_setup, db_session_path = setup_database(db_connection)
    return db_inst_setup, db_session_path

# Get command line arguments
if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "put":
        numfield = sys.argv[2]
        textfield = sys.argv[3]
        db_inst, db_session = startup_here()
        # Database write test
        print ("Writing to database...")
        logger.info('Writing/Reading from database with number "' + str(numfield) + '" and text of "' + str(textfield) + '"')
        test_database(db_inst, numfield, textfield)
    elif len(sys.argv) == 3 and sys.argv[1] == "get":
        numfield_filter = sys.argv[2]
        db_inst, db_session = startup_here()
        # Database query test
        print ("Reading from database...")
        logger.info('Reading from database filtering for number "' + str(numfield_filter) + '"')
        test_orm(db_session, numfield_filter)
    else:
        print ("Syntax:")
        print ("        " + sys.argv[0] + " put [int for 1st field] '[text for 2nd field]'")
        print ("          Run with the word put to add record using number and text")
        print ("        " + sys.argv[0] + " get [int for filter]")
        print ("          Run query filtering with supplied number")