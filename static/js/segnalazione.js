/*
# Subject to the terms of the GNU AFFERO GENERAL PUBLIC LICENSE, v. 3.0. If a copy of the AGPL was not
# distributed with this file, You can obtain one at http://www.gnu.org/licenses/agpl.txt
#
# Author: Davide Galletti                davide   ( at )   c4k.it
*/

$(document).ready(function () {
  let selectCategoria = $('select[name=categoria][id=id_categoria]');
  let helpCategoria = selectCategoria.parent().children('small');
  let helpCategoriaHtmlOriginale = helpCategoria.html()
  let inputFoto = $('input[name=foto][id=id_foto]');
  inputFoto.attr('accept', 'image/*;capture=camera');

  function hideControl(name) {
    $('input#' + name).parent().hide();
    $('textarea#' + name).parent().hide();
  }

  function showControl(name) {
    $('input#' + name).parent().show();
    $('textarea#' + name).parent().show();
  }

  selectCategoria.on('change', function () {
    let controls = ['id_nome', 'id_cognome', 'id_email', 'id_cellulare', 'id_titolo', 'id_testo', 'map', 'id_location_detail', 'id_foto', 'id_captcha_1'];
    switch (this.value) {
      case "":
        helpCategoria.html(helpCategoriaHtmlOriginale);
      case "1":
      case "2":
      case "3":
      case "20":
        controls.forEach(hideControl);
        $('input[type=submit]').hide();
        if (this.value==="1") helpCategoria.html('Per queste segnalazioni chiamare il numero 800889333 ( sempre attivo )');
        if (this.value==="2") helpCategoria.html('Per queste segnalazioni chiamare il numero 800959095 - tasto 2 (attivo dalle 8:30 alle 17:00 lun-ven)');
        if (this.value==="3") helpCategoria.html('Per queste segnalzioni chiamare il numero 800983389 ( da fisso e mobile sempre attivo )');
        if (this.value==="20") helpCategoria.html('Per le richieste relative ai servizi cimiteriali, contattare la società Fegatili SRL e Ponteverde Coperativa sociale 3367383551 - Apertura al pubblico il Lun-Ver ore 09:00-13:00 e 15:00-18:00.');
        break;
      default:
        helpCategoria.html('');
        controls.forEach(showControl);
        $('input[type=submit]').show()
        break;
    }
  });
  selectCategoria.change();
});
