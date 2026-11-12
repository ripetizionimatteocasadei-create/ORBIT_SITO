// ORBIT — età di Matteo e anni di esperienza calcolati automaticamente
// dalla data di nascita, cosi' non vanno aggiornati ogni anno a mano.
(function () {
  var BIRTHDATE = new Date(2002, 10, 5); // mese 0-indicizzato: 10 = novembre
  var START_AGE = 18; // età in cui ha iniziato a fare ripetizioni

  function computeAge(birthdate, today) {
    var age = today.getFullYear() - birthdate.getFullYear();
    var birthdayAlreadyHappened =
      today.getMonth() > birthdate.getMonth() ||
      (today.getMonth() === birthdate.getMonth() && today.getDate() >= birthdate.getDate());
    if (!birthdayAlreadyHappened) age--;
    return age;
  }

  var age = computeAge(BIRTHDATE, new Date());
  var experience = age - START_AGE;

  document.querySelectorAll('[data-dynamic="age"]').forEach(function (el) {
    el.textContent = age;
  });
  document.querySelectorAll('[data-dynamic="experience-count"]').forEach(function (el) {
    el.setAttribute("data-count", experience);
  });
  document.querySelectorAll('[data-dynamic="experience-text"]').forEach(function (el) {
    el.textContent = experience;
  });
})();
