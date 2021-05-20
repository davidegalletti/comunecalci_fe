(function($) {
  let selectCategoria = $('select[name=categoria][id=id_categoria]');

  function hideControl(name) { $('div.field-' + name).hide(); }
  function showControl(name) { $('div.field-' + name).show(); }

  selectCategoria.on('change', function() {
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
})(django.jQuery);