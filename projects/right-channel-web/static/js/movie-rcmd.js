$(function() {
    var SCROLL = 10;
    var isLoading = false;
    var more = true;
    var nextStart = 0;
    var LIMIT = 30;

    function loadNextPage() {
        loadMoreRcmds(nextStart, LIMIT);
    }
    
    function loadNextRcmd() {
        loadMoreRcmds(nextStart, 1);
    }

    function loadMoreRcmds(start, limit) {
        if (!isLoading && more) {
            isLoading = true;
            $('.ajax-loader').show();
            $.ajax({
                type : 'GET',
                url : '/api/movie/recommendation',
                dataType : 'json',
                data : {
                    start : start,
                    limit : limit
                }
            }).done(function(data) {
                manipulateView(data.movies);
                nextStart = data.start + data.total;
                if (data.limit != data.total) {
                	more = false;
                }
            }).fail(function(jqXHR) {
                if (jqXHR.status == 401) { // unauthorized
                    $.cookie.raw = true;
                    $.cookie('next', window.location.href);
                    window.location.href = '/login';
                }
            }).always(function() {
                isLoading = false; // reset the status anyway
                $('.ajax-loader').hide();
            });
        }
    }

    function manipulateView(movies) {
        var html = '';
        for (var i = 0; i < movies.length; i++) {
            var movie = movies[i];
            html += '<li>'
                +       '<div class="poster-thumbnail" data-movie-id="{0}">'.format(movie._id)
                +           '<img class="poster-medium" src="http://img3.douban.com/lpic/s25462984.jpg">'
                +           '<a class="poster-mask hide" href="/movie/{0}" title="{1}" target="_blank"></a>'.format(movie._id, movie.title)
                +           '<div class="poster-badge poster-badge-top">'
                +               '<div class="caption">{0}</div>'.format(movie.title)
                +           '</div>'
                +           '<div class="poster-badge poster-badge-bottom">'
                +               '<div class="douban-rating">'
                +                    '豆瓣评分: {0}'.format(('douban' in movie && 'rating' in movie.douban) ? movie.douban.rating : '未知')
                +                    '<a class="pull-right"><i class="icon-download-alt icon-white"></i></a>'
                +                    ('resources' in movie && 'online' in movie.resources ? '<a class="pull-right"><i class="icon-play-circle icon-white"></i></a>' : '')
                +                '</div>'
                +                '<div class="user-rating star-rating hide">'
                +                    '<a class="r1" title="给电影打0.5分" data-rating="0.5"></a>'
                +                    '<a class="r2" title="给电影打1分" data-rating="1"></a>'
                +                    '<a class="r3" title="给电影打1.5分" data-rating="1.5"></a>'
                +                    '<a class="r4" title="给电影打2分" data-rating="2"></a>'
                +                    '<a class="r5" title="给电影打2.5分" data-rating="2.5"></a>'
                +                    '<a class="r6" title="给电影打3分" data-rating="3"></a>'
                +                    '<a class="r7" title="给电影打3.5分" data-rating="3.5"></a>'
                +                    '<a class="r8" title="给电影打4.0分" data-rating="4"></a>'
                +                    '<a class="r9" title="给电影打4.5分" data-rating="4.5"></a>'
                +                    '<a class="r10" title="给电影打5分" data-rating="5"></a>'
                +               '</div>'
                +           '</div>'
                +           '<a title="想看" class="sign-btn sign-btn-plus hide" data-interest-type="wish" href="javascript:void(0)">&plus;</a>'
                +           '<a title="没兴趣" class="sign-btn sign-btn-minus hide" data-interest-type="dislike" href="javascript:void(0)">&minus;</a>'
                +       '</div>'
                +   '</li>';
        }
        $('.poster-thumbnails').append(html);
    }

    $(window).scroll(function() {
        if ($(window).scrollTop() >= $(document).height()
                - $(window).height() - SCROLL) {
            loadNextPage();
        }
    });

    $('.poster-thumbnails').on('click', '.star-rating', function(event) {
        var movieId = $(this).closest('.poster-thumbnail').attr('data-movie-id');
        var rating = $(event.target).attr('data-rating');
        $.ajax({
            type : 'POST',
            url : '/api/movie/{0}/rating'.format(movieId),
            data : {
                rating: rating
            },
            context : $(this).closest('.poster-thumbnail').closest("li") /* specify the DOM element as the context */
        }).done(function() {
            $(this).fadeOut(function() {
                loadNextRcmd();
            });
        }).fail(function(jqXHR) {
            if (jqXHR.status == 401) { // unauthorized
                $.cookie.raw = true;
                $.cookie('next', window.location.href);
                window.location.href = '/login';
            }
        });
    }).on('click', 'a[data-interest-type]', function() {
        var movieId = $(this).closest('.poster-thumbnail').attr('data-movie-id');
        var interestType = $(this).attr('data-interest-type');
        $.ajax({
            type : 'POST',
            url : '/api/movie/{0}/interest'.format(movieId),
            data : {
                type: interestType
            },
            context : $(this).closest('.poster-thumbnail').closest("li")
        }).done(function() {
            $(this).fadeOut(function() {
                loadNextRcmd();
            });
        }).fail(function(jqXHR) {
            if (jqXHR.status == 401) { // unauthorized
                $.cookie.raw = true;
                $.cookie('next', window.location.href);
                window.location.href = '/login';
            }
        });
    }).on('mouseenter', '.poster-thumbnail', function() {
        $(this).find('.poster-mask').removeClass('hide');
        $(this).find('.douban-rating').addClass('hide');
        $(this).find('.user-rating').removeClass('hide');
        $(this).find('.sign-btn').removeClass('hide');
    }).on('mouseleave', '.poster-thumbnail', function() {
        $(this).find('.poster-mask').addClass('hide');
        $(this).find('.douban-rating').removeClass('hide');
        $(this).find('.user-rating').addClass('hide');
        $(this).find('.sign-btn').addClass('hide');
    });
    
    loadNextPage();
});