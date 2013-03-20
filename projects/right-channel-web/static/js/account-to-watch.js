/** *** account: to watch list **** */
$(function () {
    $('table').on('click', '#watched', function (e) {
        var $btn = $(this);
        if (!$btn.hasClass('disabled')) {
            var movie_id = $btn.attr('data-id');
            $btn.addClass('disabled');
            $.ajax({
                type: 'POST',
                url: '/api/movie/watched',
                data: {
                    id: movie_id
                }
            }).done(function () {
                $btn.parents('tr').fadeOut(function () {
                    if ($('table tbody tr:visible').length === 0)
                        $('table').hide();
                    else
                        $('#movieCount').text($('table tbody tr:visible').length);
                    $('#movieCount').text($('table tbody tr:visible').length);
                });
            }).always(function () {
                $btn.removeClass('disabled');
            });
        }
    });

    $('table').on('click', '#remove', function (e) {
        var $btn = $(this);
        if (!$btn.hasClass('disabled')) {
            var movie_id = $btn.attr('data-id');
            $btn.addClass('disabled');
            $.ajax({
                type: 'delete',
                url: '/api/movie/towatch/' + movie_id
            }).done(function () {
                $btn.parents('tr').fadeOut(function () {
                    if ($('table tbody tr:visible').length === 0)
                        $('table').hide();
                    else
                        $('#movieCount').text($('table tbody tr:visible').length);
                    $('#movieCount').text($('table tbody tr:visible').length);
                });
            }).always(function () {
                $btn.removeClass('disabled');
            });
        }
    });
});