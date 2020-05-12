// Этот код позволяет использовать функцию jQuery.style(name, value, priority),
// где priority - это important или же ничего. В чистом JQuery нет возможности
// задать этот флаг.
// Взято с
// https://stackoverflow.com/questions/2655925/how-to-apply-important-using-css
// Aram Kocharyan
(function($) {
  if ($.fn.style) {
    return;
  }

  // Escape regex chars with \
  var escape = function(text) {
    return text.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, "\\$&");
  };

  // For those who need them (< IE 9), add support for CSS functions
  var isStyleFuncSupported = !!CSSStyleDeclaration.prototype.getPropertyValue;
  if (!isStyleFuncSupported) {
    CSSStyleDeclaration.prototype.getPropertyValue = function(a) {
      return this.getAttribute(a);
    };
    CSSStyleDeclaration.prototype.setProperty = function(styleName, value,
                                                         priority) {
      this.setAttribute(styleName, value);
      var priority = typeof priority != 'undefined' ? priority : '';
      if (priority != '') {
        // Add priority manually
        var rule = new RegExp(escape(styleName) + '\\s*:\\s*' + escape(value) +
            '(\\s*;)?', 'gmi');
        this.cssText =
            this.cssText.replace(
                rule, styleName + ': ' + value + ' !' + priority + ';'
            );
      }
    };
    CSSStyleDeclaration.prototype.removeProperty = function(a) {
      return this.removeAttribute(a);
    };
    CSSStyleDeclaration.prototype.getPropertyPriority = function(styleName) {
      var rule = new RegExp(escape(styleName) + '\\s*:\\s*[^\\s]*\\s*!important(\\s*;)?',
          'gmi');
      return rule.test(this.cssText) ? 'important' : '';
    }
  }

  // The style function
  $.fn.style = function(styleName, value, priority) {
    // DOM node
    var node = this.get(0);
    // Ensure we have a DOM node
    if (typeof node == 'undefined') {
      return this;
    }
    // CSSStyleDeclaration
    var style = this.get(0).style;
    // Getter/Setter
    if (typeof styleName != 'undefined') {
      if (typeof value != 'undefined') {
        // Set style property
        priority = typeof priority != 'undefined' ? priority : '';
        style.setProperty(styleName, value, priority);
        return this;
      } else {
        // Get style property
        return style.getPropertyValue(styleName);
      }
    } else {
      // Get CSSStyleDeclaration
      return style;
    }
  };
})(jQuery);
// Тоже взято с интернета
String.prototype.replaceAll = function (find, replace) {
    return this.replace(new RegExp(find, 'g'), replace);
}

let formatTemplate = /(?<=^|[^/]){(.*?)(?<=[^/])}/g;
let escapedBracket = /\/([{}])/g;

String.prototype.format = function() {
  data = arguments[arguments.length - 1];
  return this.replace(
    formatTemplate, (entry, word) => arguments[word] || data[word] || entry)
                                     .replace(escapedBracket,
                                              (entry, word) => word);
};

var scrollEvents = ['wheel', 'mousewheel']

// При попытке прокрутить страницу, наведясь на один из переданных в функцию
// элементов, будет прокручиваться только содержимое этого элемента, но не
// страницы.
function freezeScroll(){
    for (var i = 0; i < arguments.length; i++) {
        elem = arguments[i];
        let func = preventScrollEventFunc(elem);
        let options = {passive: false};
        $(elem).on('mouseenter', function(){
            onWheel(window, func, options);
        }).on('mouseleave', function(){
            removeOnWheel(window, func);
        });
    }
}
// Отменить скролл страницы, если элемент selector прокручен до упора
function preventScrollEventFunc(selector){
    let elem = $(selector);
    function preventScroll(e){
        let offset = e.wheel || e.wheelDelta;
        let crossingUpper = elem.scrollTop() == 0 && offset > 0;
        let crossingDown = (elem[0].scrollHeight - elem.scrollTop() ==
            elem[0].clientHeight && offset < 0);
        if (crossingUpper || crossingDown){
            e.preventDefault()
        }
    }
    return preventScroll;
}
// Повесить обработчик func для событий wheel и mousewheel у elem
function onWheel(elem, func, options){
    options = options || {};
    scrollEvents.forEach(function(item, i, arr){
        elem.addEventListener(item, func, options);
    });
}
// Убрать обработчик func для событий wheel и mousewheel у elem
function removeOnWheel(elem, func, options){
    options = options || {};
    scrollEvents.forEach(function(item, i, arr){
        elem.removeEventListener(item, func, options);
    });
}
// Отменяем событие e
function preventDefault(e){
    e.preventDefault();
}

function switchDisplay(selector){
    let elem = $(selector);
    let currentDisplay = elem.css('display');
    if (currentDisplay == 'none'){
        elem.style('display', elem.css('--display') || 'block', 'important');
        elem.css('--display', 'none');
    }
    else {
        elem.css('--display', currentDisplay);
        elem.style('display', 'none', 'important');
    }
}

function forEach(sequence, func){
    for (let i = 0;i < sequence.length; i++){
        func(sequence[i], i, sequence);
    }
}

let win = $(window);
let onAppearEvents = new Map();
let onDisappearEvents = new Map();
//отслеживаем событие прокрутки страницы

function isVisible(elem){
    return win.scrollTop() + win.height() >= $(elem).offset().top;
}

function execAppearHandler(elem, handler, params, handlers){
    $.proxy(handler, elem)();
    if (params.once){
        handlers.delete(handler);
    }
}


win.scroll(function() {
    // Складываем значение прокрутки страницы и высоту окна, этим мы получаем
    // положение страницы относительно нижней границы окна, потом проверяем,
    // если это значение больше, чем отступ нужного элемента от верха страницы,
    // то значит элемент уже появился внизу окна, соответственно виден
    onAppearEvents.forEach(function(handlers, elem){
        if (isVisible(elem)) {
            handlers.forEach(function(params, handler){
                execAppearHandler(elem, handler, params, handlers);
            });
        }
    });
    onDisappearEvents.forEach(function(handlers, elem, map){
        if (!isVisible(elem)) {
            handlers.forEach(function(params, handler){
                execAppearHandler(elem, handler, params, handlers);
            });
        }
    });
});

function appearFunc(eventsMap){
    return function (handler, params={once: false}){
        if (this){
            let handlers = eventsMap.get(this) || new Map();
            handlers.set(handler, params);
            eventsMap.set(this, handlers);
        }
    }
}

$.prototype.appear = appearFunc(onAppearEvents);
$.prototype.disappear = appearFunc(onDisappearEvents);

Array.prototype.remove = function() {
    var what, a = arguments, L = a.length, ax;
    while (L && this.length) {
        what = a[--L];
        while ((ax = this.indexOf(what)) !== -1) {
            this.splice(ax, 1);
        }
    }
    return this;
};

// Возвращает строку с полным именем пользователя user
function fullUserName(user){
    return [user.second_name, user.first_name].join(' ');
}

// Проверка схожести объектов по их полям
function isEqual(obj1, obj2){
    for (let prop in obj1){
        if (obj1[prop] != obj2[prop]){
            return false;
        }
    }
    return true;
}