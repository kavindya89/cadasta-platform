$('button#add-party').click(function() {
  $('div#select-party').toggleClass('hidden');
  $('div#new-item').toggleClass('hidden');
});

$('table#select-list tr').click(function(event) {
  var target = $(event.target).closest('tr');
  var relId = target.attr('data-id');
  target.closest('tbody').find('tr.info').removeClass('info');
  target.addClass('info');
  $('input[name="id"]').val(relId);
});
