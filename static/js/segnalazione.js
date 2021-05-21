/*
# Subject to the terms of the GNU AFFERO GENERAL PUBLIC LICENSE, v. 3.0. If a copy of the AGPL was not
# distributed with this file, You can obtain one at http://www.gnu.org/licenses/agpl.txt
#
# Author: Davide Galletti                davide   ( at )   c4k.it
*/

$(document).ready(function () {
  let selectCategoria = $('select[name=categoria][id=id_categoria]');
  let inputFoto = $('input[name=foto][id=id_foto]');
  inputFoto.attr('accept', 'image/*;capture=camera');

  function hideControl(name) {
    $('div.field-' + name).hide();
  }

  function showControl(name) {
    $('div.field-' + name).show();
  }

  selectCategoria.on('change', function () {
    if (this.value === '') {
      let showControls = [''];
      let hideControls = [''];
      showControls.forEach(showControl);
      hideControls.forEach(hideControl);
    } else {
      let showControls = [''];
      let hideControls = [''];
      showControls.forEach(showControl);
      hideControls.forEach(hideControl);
    }
  });
});
