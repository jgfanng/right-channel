$(function() {
  var emailRE = /^[a-zA-Z0-9._%+-]+@([a-zA-Z0-9-]+\.)+[a-zA-Z0-9]{2,4}$/;

  // email validation
  $('#email').focus(function(event) {
    $('#emailHelp').text('请输入您的常用邮箱，用来登录Right Channel');
    $('#emailHelp').attr('class', 'help-inline help-info');
    $('#emailHelp').show();
  });

  $('#email').blur(function(event) {
    var $target = $(event.target);
    var value = $.trim($target.val());

    if (value.length == 0) {
      $('#emailHelp').text('邮箱不能为空');
      $('#emailHelp').attr('class', 'help-inline help-error');
      $('#emailHelp').show();
    } else if (value.length > 254) {
      $('#emailHelp').text('邮箱不多于254个字符');
      $('#emailHelp').attr('class', 'help-inline help-error');
      $('#emailHelp').show();
    } else if (!emailRE.test(value)) {
      $('#emailHelp').text('邮箱格式不正确');
      $('#emailHelp').attr('class', 'help-inline help-error');
      $('#emailHelp').show();
    } else {
      $('#emailHelp').text('');
      $('#emailHelp').attr('class', 'help-inline help-info');
      $('#emailHelp').hide();
    }
  });

  // password validation
  $('#password').focus(function(event) {
    $('#passwordHelp').text('6-16个字符，建议使用字母、数字或符号的组合');
    $('#passwordHelp').attr('class', 'help-inline help-info');
    $('#passwordHelp').show();
  });

  $('#password').blur(function(event) {
    var $target = $(event.target);
    var value = $target.val();

    if (value.length == 0) {
      $('#passwordHelp').text('密码不能为空');
      $('#passwordHelp').attr('class', 'help-inline help-error');
      $('#passwordHelp').show();
    } else if (value.length < 6) {
      $('#passwordHelp').text('密码不足6个字符');
      $('#passwordHelp').attr('class', 'help-inline help-error');
      $('#passwordHelp').show();
    } else if (value.length > 16) {
      $('#passwordHelp').text('密码不多于16个字符');
      $('#passwordHelp').attr('class', 'help-inline help-error');
      $('#passwordHelp').show();
    } else {
      $('#passwordHelp').text('');
      $('#passwordHelp').attr('class', 'help-inline help-info');
      $('#passwordHelp').hide();
    }
  });

  // nick name validation
  $('#nickName').focus(function(event) {
    $('#nickNameHelp').text('请输入您在网上的常用昵称，不多于12个字符');
    $('#nickNameHelp').attr('class', 'help-inline help-info');
    $('#nickNameHelp').show();
  });

  $('#nickName').blur(function(event) {
    var $target = $(event.target);
    var value = $target.val();

    if (value.length == 0) {
      $('#nickNameHelp').text('昵称不能为空');
      $('#nickNameHelp').attr('class', 'help-inline help-error');
      $('#nickNameHelp').show();
    } else if (value.length > 12) {
      $('#nickNameHelp').text('昵称不多于12个字符');
      $('#nickNameHelp').attr('class', 'help-inline help-error');
      $('#nickNameHelp').show();
    } else {
      $('#nickNameHelp').text('');
      $('#nickNameHelp').attr('class', 'help-inline help-info');
      $('#nickNameHelp').hide();
    }
  });

  // form submission validation
  $('#register').submit(
      function() {
        var emailValue = $.trim($('#email').val());
        var pwsswordValue = $('#password').val();
        var nickNameValue = $('#nickName').val();

        if (emailValue.length > 0 && emailValue.length <= 254
            && emailRE.test(emailValue) && passwordValue.length >= 6
            && passwordValue.length <= 16 && nickNameValue.length > 0
            && nickNameValue.length <= 12)
          return true;
        else {
          $('#submitHelp').text('您输入的内容不正确，请重新输入')
          $('#submitHelp').attr('class', 'help-inline help-error');
          $('#submitHelp').show().fadeOut(2000);
          return false;
        }
      });
});