"""
Created on Mon July 10, 2017

@author: Ruchika Chhabra
"""

from ConfigParser import ConfigParser

class ConfigParse():
    '''
    DESCRIPTION:
    ------------
    This class reads config.ini file and sets the required user inputs
    in the class attributes.

    ATTRIBUTES:
    ----------
    1. ES_Host (string)      : Elasticsearch host IP
    2. ES_Port (string)      : Elasticsearch port which is 5601 by default
    3. Index_Name (string)   : Elasticsearch index name
    4. Type_Name (string)    : Elasticsearch index type
    5. Mapping_File (string) : Mapping file to used for creating the ES index.
    6. del_flag (int)        : Can take values 1 and 0 to delete the already existing
                               elasticsearch index or not respectively.
    7. Index_ID              : Index ID from which documents should be inserted
                               to ES.
    8. URL_File              : List of URLs to be scraped.
    '''

    def __init__(self):
        '''
        DESCRIPTION:
        ------------
        This method declares the class attributes.
        '''
        self.ES_Host      = None
        self.ES_Port      = None
        self.Index_Name   = None
        self.Type_Name    = None
        self.Mapping_File = None
        self.Index_ID     = None
        self.del_flag     = None
        self.URL_File     = None

    def configReader(self):
        '''
        DESCRIPTION:
        -----------
        * This method parses the config file and read the variables defined by
          the user in the config.ini file.
        * The values of the variables are then set in the corresponding class
          attributes.
        '''
        parser = ConfigParser(allow_no_value=True)
        # Read config.ini
        parser.read('config.ini')

        # Define ES Instance config variables.
        self.ES_Host      = parser.get('ES Config Variables', 'es_host')
        self.ES_Port      = int(parser.get('ES Config Variables', 'es_port'))
        self.Index_Name   = parser.get('ES Config Variables', 'index_name')
        self.Type_Name    = parser.get('ES Config Variables', 'type_name')
        self.Mapping_File = parser.get('ES Config Variables', 'mapping_file')
        self.Index_ID     = int(parser.get('ES Config Variables', 'index_id'))
        self.del_flag     = int(parser.get('ES Config Variables', 'delete_index'))

        # Read input variables for the code
        self.URL_File     = parser.get('Input Variables', 'url_list')

    def updateConfigParam(self, param,  value):
        '''
        DESCRIPTION:
        ------------
        This method updates the value of param in the config.ini file.

        PARAMETERS:
        ---------
        param (string): Config Parameter to be updated.
        value (string) Value of Config Parameter to be set.
        '''

        config = ConfigParser(allow_no_value=True)
        config.read('config.ini')
        config.set('ES Config Variables', param, value)
        with open('config.ini', 'wb') as configfile:
            config.write(configfile)
