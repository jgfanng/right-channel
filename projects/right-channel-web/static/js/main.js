$(function () {
    $('#content').on('click', '#toWatch', function (e) {
        var $btn = $(this);
        if (!$btn.hasClass('disabled')) {
            var movie_id = $btn.attr('data-id');
            $btn.addClass('disabled');
            $.ajax({
                type: 'POST',
                url: '/api/movie/towatch',
                data: {
                    id: movie_id
                }
            }).done(function () {
            	  $btn.attr('id', 'toUnwatch');
                $btn.addClass('btn-inverse');
                $btn.children('i').attr('class', 'icon-remove icon-white');
            }).fail(function (jqXHR) {
                if (jqXHR.status == 401) { // unauthorized
                    $.cookie.raw = true;
                    $.cookie('next', window.location.href);
                    window.location.href = '/login';
                }
            }).always(function () {
                $btn.removeClass('disabled');
            });
        }
    }).on('click', '#toUnwatch', function (e) {
        var $btn = $(this);
        if (!$btn.hasClass('disabled')) {
            var movie_id = $btn.attr('data-id');
            $btn.addClass('disabled');
            $.ajax({
                type: 'delete',
                url: '/api/movie/towatch/' + movie_id,
                data: {
                    id: movie_id
                }
            }).done(function () {
            	  $btn.attr('id', 'toWatch');
                $btn.removeClass('btn-inverse');
                $btn.children('i').attr('class', 'icon-ok');
            }).always(function () {
                $btn.removeClass('disabled');
            });
        }
    }).on('click', '#watched', function (e) {
        var $btn = $(this);
        if (!$btn.hasClass('disabled')) {
            var movie_id = $btn.attr('data-id');
            $btn.addClass('disabled');
            $.ajax({
                type: 'post',
                url: '/api/movie/watched',
                data: {
                    id: movie_id
                }
            }).done(function () {
            	  $btn.attr('id', 'unwatched');
                $btn.addClass('btn-inverse');
                $btn.children('i').attr('class', 'icon-remove icon-white');
            }).fail(function (jqXHR) {
                if (jqXHR.status == 401) { // unauthorized
                    $.cookie.raw = true;
                    $.cookie('next', window.location.href);
                    window.location.href = '/login';
                }
            }).always(function () {
                $btn.removeClass('disabled');
            });
        }
    });
});