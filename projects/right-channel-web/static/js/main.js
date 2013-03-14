$(function () {
    $('#content ul.gallery').click(

    function (e) {
        var $btn = $(e.target);
        if ($btn.prop('nodeName') == 'I') {
            $btn = $btn.parent();
        }
        if ($btn.length === 0 || $btn.attr('id') != 'toWatch') {
            return false;
        }
        var movie_id = $btn.attr('data-id');
        $btn.attr('disabled', 'disabled');
        $btn.addClass('disabled');
        $.ajax({
            type: 'POST',
            url: '/api/movie/towatch',
            data: {
                id: movie_id
            }
        }).done(function () {
            alert('success');
        }).fail(function (jqXHR) {
            if (jqXHR.status == 401) {
                window.location.href = '/login';
            }
        });
    });
});