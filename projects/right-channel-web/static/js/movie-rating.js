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
            var posterImg = '<a href="/movie/{0}" target="_blank"><img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQQAAAC0CAYAAABytVLLAAAIhElEQVR4Xu3avYsUWxMH4N7AL9DARM1EDNVQBP99IxMxUoxFMJBFENHAj/ftgbO07cxsrXW99K16TMT1TM2pp7p/0907J6enpz8nfwgQIPB/gROB4DggQGAICATHAgECZwICwcFAgIBAcAwQIPC7gCsERwUBAq4QHAMECLhCcAwQIHBEwC2Dw4MAAbcMjgECBNwyOAYIEHDL4BggQCAi4BlCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgbHDQr1+/nt69e3e2sxs3bkxPnjz5Zaenp6fTy5cvpx8/fux+vm/N27dvpzdv3py97t69e9P9+/f/uOMXL15M8/vevn17evTo0S91xv+NH+5b80/v548b8cKDAgJhYwfH+sQa21ue8Osw2HcSrk++seZPQ2FZb32yrwPs39jPxsZWZjsCYUOj/Pbt2/Ts2bPp+/fv0zhxlyfiw4cPp1u3bk3Pnz+fPn/+/Nuak5OT6enTp9OVK1fO1oyTd5y0V69e3V1tXLp0Kdz5sU//5Z7X7/W39hPeuIUXFhAIFyb7ey8YJ/84ka5duzatQ+Lu3bu70JhvFeaTf16z/rO8gphD5M6dO7tL/fkW4+fPn7vXffny5eyWY4TP+nXL8JnfYw6Tr1+//nLLsNxf5L0OrdnXx9+TVvmQgEDY+LGxPkkvX768O5Hnv+cT9OPHj7sOlpfx65N/HSzjpByf/HOdx48fT/O/5yuPUWsOnflq5Pr169ODBw9+u+qY33esWb5ufTXy6dOnX8Lo0H42PooW2xMIGx7z8mQbzxAOPRuY21ivOXalMT9cXH66z1cR79+/n5avWdLsO/HH/y/rjJ8t60SufDIPOzc8wv/c1gTCRke2PAH3nVzzttfPGca6Dx8+7H67cF4gzDWiT/6PBcJ5DzAFwkYPsj3bEggbnNWhMJi3GrkdGLcV43nBsUv05af7oauDQ7cG88+PPQgd9cbzish+NjiOVlsSCBsb97EwuGggzLXOe4i3/pXhvu8PHAuEyKf/zZs3zx5gnrefjY2j3XYEwsZGPh70XeRefn1SRn/tuLzamB8avnr1aveQcJy0kWcIy4eekV+V/hO/Bt3YyEptRyBsaJyHvnA0trjvhFtuf/npft59feS3A8vvKhx6hrD8+Zpy+WWq8/azoTG03opA2ND4D33jbx0Iy1uH8dXli35VeLzXoQeP63rHHirO+1l/eenf+Cr1hkZXZisCocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgL/A/1uMQYymAtG0AAAAASUVORK5CYII=" class="poster-medium"></a>'.format(movie._id);
            var topBadge = '<div class="poster-badge poster-badge-top"><div class="caption">{0}</div></div>'.format(movie.title);
            var bottomBadge = '<div class="poster-badge poster-badge-bottom">'
                +                '<div class="user-rating">'
                +                    '<a title="想看" class="pull-left" data-interest-type="wish" href="javascript:void(0)"><i class="icon-plus-sign icon-white"></i></a>'
                +                    '<div class="star-rating pull-left">'
                +                        '<a class="r1" title="给电影打0.5分" data-rating="0.5"></a>'
                +                        '<a class="r2" title="给电影打1分" data-rating="1"></a>'
                +                        '<a class="r3" title="给电影打1.5分" data-rating="1.5"></a>'
                +                        '<a class="r4" title="给电影打2分" data-rating="2"></a>'
                +                        '<a class="r5" title="给电影打2.5分" data-rating="2.5"></a>'
                +                        '<a class="r6" title="给电影打3分" data-rating="3"></a>'
                +                        '<a class="r7" title="给电影打3.5分" data-rating="3.5"></a>'
                +                        '<a class="r8" title="给电影打4.0分" data-rating="4"></a>'
                +                        '<a class="r9" title="给电影打4.5分" data-rating="4.5"></a>'
                +                        '<a class="r10" title="给电影打5分" data-rating="5"></a>'
                +                    '</div>'
                +                    '<a title="没兴趣" class="pull-right" data-interest-type="dislike" href="javascript:void(0)"><i class="icon-minus-sign icon-white"></i></a>'
                +                '</div>'
                +            '</div>';
            html += '<li><div class="poster-thumbnail" data-movie-id="{0}">{1}{2}{3}</div></li>'.format(movie._id, posterImg, topBadge, bottomBadge);
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
    });
    
    loadNextPage();
});