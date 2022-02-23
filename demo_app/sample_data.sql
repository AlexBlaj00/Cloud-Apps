---- Create the app

insert into apps(id, name, link) values(3,"Small server", "127.0.0.1:1337");

---- Create the permissions

insert into permissions(id, name, description, app_id) values(4, "CREATE data", "Permission to create new data", 3);
insert into permissions(id, name, description, app_id) values(5, "READ data", "Permission to read data", 3);
insert into permissions(id, name, description, app_id) values(6, "UPDATE data", "Permission to update data", 3);
insert into permissions(id, name, description, app_id) values(7, "DELETE data", "Permission to delete data", 3);

---- Create the groups

insert into groups(id, name, description) values(3, "Owners of Small servers", "Users are the owners of the Small server");
insert into groups(id, name, description) values(4, "Editors of Small servers", "Users are the editors of the Small server");
insert into groups(id, name, description) values(5, "Viewers of Small servers", "Users can only view the Small server");

---- Link the permissions to the groups

INSERT INTO groups_perm_relation(group_id, perm_id) values(3,4);
INSERT INTO groups_perm_relation(group_id, perm_id) values(3,5);
INSERT INTO groups_perm_relation(group_id, perm_id) values(3,6);
INSERT INTO groups_perm_relation(group_id, perm_id) values(3,7);
INSERT INTO groups_perm_relation(group_id, perm_id) values(4,5);
INSERT INTO groups_perm_relation(group_id, perm_id) values(4,6);
INSERT INTO groups_perm_relation(group_id, perm_id) values(5,5);

---- Create the users

INSERT INTO users VALUES (8,'jdoe','$5$rounds=535000$pIIZjh0OBbM9jvGs$h3aeOUR2H6m.hDzJzlSo1Sc5uKrFA9EsKN0Nd9.1u/4','John Doe','jdoe@yahoo.com','0747553214',NULL),(9,'jadoe','$5$rounds=535000$ifC3P50afQtJ77dC$r0KOb7J786FAxqxyVzrEMiAPK6tmOyYWJjBKCV/TjE4','Jane Doe','jadoe@yahoo.com','0758314679',NULL),(10,'asmith','$5$rounds=535000$.lGpw41WUTC8igSe$LypTB6Yu1EdM4SNFfFu0ST/nIS22Iez/ogldzlCagKB','Adam Smith','asmith@yahoo.com','0734658214',NULL);

---- Link the users to the groups

insert into user_groups_relation(user_id, group_id) values(8, 3);
insert into user_groups_relation(user_id, group_id) values(9, 4);
insert into user_groups_relation(user_id, group_id) values(10, 5);

