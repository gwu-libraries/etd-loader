# etd-loader
Application for loading ETDs into GW ScholarSpace

etd-loader performs the following functions:
* Retrieves ETD files via sFTP from a remote server.
* Import ETDs into GW ScholarSpace.
* Creates MARC records for ETDs.

## Setup
0. Install prerequisite system packages needed for cryptography as per https://cryptography.io/en/latest/installation.  For Ubuntu, this would look like:

        sudo apt-get install build-essential libssl-dev libffi-dev python3-devk

1. Get this code.

        git clone https://github.com/gwu-libraries/etd-loader.git

2. Create a virtualenv.

        virtualenv -p python3 ENV
        source ENV/bin/activate
    
3. Install dependencies.

        pip install -r requirements.txt
    
4. Copy configuration file.

        cp example.config.py config.py
    
5. Edit configuration file. The file is annotated with descriptions of the configuration options.

## Directory structure

        / <base path>
            / etd_store # Contains ETD files that have been retrieved from ETD FTP
            / import_store # Contains files to be imported into repository
            / marc_store # Contains previously created MARC records
            / etd_to_be_imported # Contains ETD files that are to be imported into repository
            / etd_to_be_marced # Contains ETD files that are to be crosswalked to MARC records
            id.db #Id Store, a sqlite db mapping repository ids to Proquest ids.

## Running
To run etd-loader:

    python etd_loader.py
    
To run single steps:

    python etd_loader.py --only <retrieve or import or marc>
    
Running all steps will:
1. Retrieve ETD files from the remote server.
    1. For every ETD file that is on the remote server but not in the `etd-store`, copy from remote server to `etd-store`.
    2. For every ETD files that is retrieved, copy from `etd-store` to `etd_to_be_marced` and `etd_to_be_imported`.
2. Import ETDs into GW ScholarSpace. For every ETD file in `etd_to_be_imported`:
    1. Crosswalk Proquest metadata to repository metadata.
    2. Extract files from ETD file.
    3. Execute GW Scholarspace import function.
    4. Store the returned repository id in the Id Store.
    5. Delete the ETD file from `etd_to_be_imported`.
3. Create MARC records for the ETDs.
    1. For every ETD file in `etd_to_be_marced`:
        1. Check if there is a repository id in the Id Store. If not, then skip.
        2. Crosswalk Proquest metadata and repository id to MARC.
        3. Append MARC record to temporary MARC record file.
        4. Delete the ETD file from `etd_to_be_marced`.
    2. Email the temporary MARC record file.
    3. Move the temporary MARC record file to `marc_store`.
    
## Reprocessing ETD files
To reprocess ETD files, the following can be used:
* Place the new ETD file on the remote server and delete old from `etd_store`. On next run, the ETD file will be
  retrieved, imported into GW ScholarSpace (using the existing repository id), and a new MARC record will be generated.
* To just re-import into GW ScholarSpace, add the ETD file to `etd_to_be_imported` and execute `python etd-loader.py --only import`.
* To just generate a new MARC record, add the ETD file to `etd_to_be_marced` and execute `python etd-loader.py --only marc`.

    
