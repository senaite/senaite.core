CREATE SEQUENCE content_sequence;

CREATE TABLE content (
	content_id INTEGER NOT NULL, 
	id VARCHAR(256) NOT NULL, 
	content_uid VARCHAR(36) NOT NULL, 
	object_type VARCHAR(64), 
	status VARCHAR(64), 
	portal_type VARCHAR(64), 
	folder_position INTEGER, 
	container_id INTEGER, 
	path TEXT, 
	relative_path TEXT, 
	title TEXT, 
	description TEXT, 
	subject TEXT, 
	location TEXT, 
	contributors TEXT, 
	creators TEXT, 
	creation_date TIMESTAMP, 
	modification_date TIMESTAMP, 
	effectivedate TIMESTAMP, 
	expirationdate TIMESTAMP, 
	language TEXT, 
	rights TEXT, 
	excludefromnav BOOLEAN, 
	PRIMARY KEY (content_id), 
	FOREIGN KEY(container_id) REFERENCES content (content_id) ON DELETE CASCADE 
);

CREATE UNIQUE INDEX content_content_uid_idx ON content (content_uid);

CREATE INDEX content_modification_date_idx ON content (modification_date);

CREATE TABLE files (
	content_id INTEGER NOT NULL, 
	attribute VARCHAR(156) NOT NULL, 
	type VARCHAR(30), 
	content OID, 
	path VARCHAR(300), 
	file_size INTEGER, 
	checksum VARCHAR(33), 
	file_name VARCHAR(156), 
	mime_type VARCHAR(80), 
	PRIMARY KEY (content_id, attribute), 
	FOREIGN KEY(content_id) REFERENCES content (content_id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX files_idx ON files (content_id, attribute);

CREATE TABLE relations (
	source_id INTEGER NOT NULL, 
	target_id INTEGER NOT NULL, 
	relationship VARCHAR(128) NOT NULL, 
	PRIMARY KEY (source_id, target_id, relationship), 
	FOREIGN KEY(source_id) REFERENCES content (content_id) ON DELETE CASCADE, 
	FOREIGN KEY(target_id) REFERENCES content (content_id) ON DELETE CASCADE
);

GRANT ALL on relations to zodbuser;

CREATE TABLE  atdocument (
	content_id INTEGER NOT NULL, 
	text TEXT, 
	presentation TEXT, 
	tablecontents TEXT, 
	PRIMARY KEY (content_id)
);

GRANT ALL ON atdocument to zodbuser;


CREATE TABLE  atbtreefolder (
	content_id INTEGER NOT NULL, 
	constraintypesmode INTEGER, 
	locallyallowedtypes TEXT, 
	immediatelyaddabletypes TEXT, 
	PRIMARY KEY (content_id)
);

GRANT ALL ON atbtreefolder to zodbuser;
