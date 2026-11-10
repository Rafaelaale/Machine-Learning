// Cria banco do app
db = db.getSiblingDB("burguer_app_db");

// Cria usuário do Mongo para o app
db.createUser({
  user: "appuser",
  pwd: "apppass",
  roles: [{ role: "readWrite", db: "burguer_app_db" }]
});

