$(function() {
    var SCROLL = 10;
    var isLoading = false;
    var more = true;
    var nextStart = 0;
    var CANDIDATES = 100;
    var PICK = 30;

    function loadNextPage() {
        loadMoreRatings(nextStart, nextStart + CANDIDATES, PICK);
    }
    
    function loadNextRating() {
        loadMoreRatings(nextStart, nextStart + 1, 1);
    }

    function loadMoreRatings(start, end, pick) {
        if (!isLoading && more) {
            isLoading = true;
            $('.ajax-loader').show();
            $.ajax({
                type : 'GET',
                url : '/api/movie/rating-candidate',
                dataType : 'json',
                data : {
                    start : start,
                    end: end,
                    pick: pick
                }
            }).done(function(data) {
                manipulateView(data.movies);
                nextStart = data.end;
                if (data.total == 0) {
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
            var posterImg = '<a href="/movie/{0}" target="_blank"><img src="http://img3.douban.com/lpic/s11356673.jpg" class="poster-medium"></a>'.format(movie._id);
            var topBadge = '<div class="poster-badge poster-badge-top"><div class="caption">{0}</div></div>'.format(movie.title);
            var bottomBadge = '<div class="poster-badge poster-badge-bottom hide">'
                +                 '<div class="user-rating star-rating">'
                +                     '<a class="r1" title="给电影打0.5分" data-rating="0.5"></a>'
                +                     '<a class="r2" title="给电影打1分" data-rating="1"></a>'
                +                     '<a class="r3" title="给电影打1.5分" data-rating="1.5"></a>'
                +                     '<a class="r4" title="给电影打2分" data-rating="2"></a>'
                +                     '<a class="r5" title="给电影打2.5分" data-rating="2.5"></a>'
                +                     '<a class="r6" title="给电影打3分" data-rating="3"></a>'
                +                     '<a class="r7" title="给电影打3.5分" data-rating="3.5"></a>'
                +                     '<a class="r8" title="给电影打4.0分" data-rating="4"></a>'
                +                     '<a class="r9" title="给电影打4.5分" data-rating="4.5"></a>'
                +                     '<a class="r10" title="给电影打5分" data-rating="5"></a>'
                +                '</div>'
                +            '</div>';
            var interestBtn = '<a title="想看" class="interest-btn interest-btn-close hide" data-interest-type="wish" href="javascript:void(0)"></a>';
            html += '<li><div class="poster-thumbnail" data-movie-id="{0}">{1}{2}{3}{4}</div></li>'.format(movie._id, posterImg, topBadge, bottomBadge, interestBtn);
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
                loadNextRating();
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
                loadNextRating();
            });
        }).fail(function(jqXHR) {
            if (jqXHR.status == 401) { // unauthorized
                $.cookie.raw = true;
                $.cookie('next', window.location.href);
                window.location.href = '/login';
            }
        });
    }).on('mouseenter', '.poster-thumbnail', function() {
        $(this).find('.poster-badge-bottom').stop().fadeIn();
        $(this).find('.interest-btn').stop().show();
    }).on('mouseleave', '.poster-thumbnail', function() {
        $(this).find('.poster-badge-bottom').stop().hide();
        $(this).find('.interest-btn').stop().hide();
    });
    
    loadNextPage();
});