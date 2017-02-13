CREATE VIEW `prod_cons` AS
  SELECT PRODid, CONSid, c.topic, c.timestamp FROM CONS C  join PROD p on c.dataID = p.dataId and c.timestamp = p.timestamp 
