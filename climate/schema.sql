drop table if exists climate;
create table climate (
  id integer primary key autoincrement,
  'date' date not null,
  'rainfall' number not null,
  'temperature' number not null
);
insert into climate (date, rainfall, temperature) values ('01/01/1111', 111, 111);