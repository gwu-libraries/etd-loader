# The path in which to locally store ETD files
base_path = "/tmp/etd"
# Information on the remote ETD server
etd_ftp_host = "gwetdsftp-prod.wrlc.org"
etd_ftp_username = "username"
etd_ftp_password = "password"
etd_ftp_path = "/opt/proquest-test"
etd_ftp_port = 22
# Configuration for sending email
mail_host="smtp.gmail.com"
mail_port = 587
mail_username = "username@email.gwu.edu"
mail_password = "password"
# Where to send MARC records
marc_mail_to = "rdg@gwu.edu"
# GW ScholarSpace ingest configuration
ingest_path = "/opt/gwss"
ingest_command = "rake"
repo_base_url = "https://scholarspace.library.gwu.edu/etd/"
