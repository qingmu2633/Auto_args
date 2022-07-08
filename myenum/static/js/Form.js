function Form(options) {
    const defaultOptions = {
        container: '',
        defaultValue: {},
        events: {}
    }

    this._selectMap = {};

    if (typeof options === 'string') {
        const container = options;
        options = {
            container: container
        }
    } 

    this.options = Object.assign(defaultOptions, options);

    
    this.formElement = $(this.options.container);
    this.init(this.options)
}

Form.prototype.init = function(options) {
    this.initSelect();
    this.initEvent(options.events)
    this.initUpload();
}

Form.prototype.initDefaultVal = function() {

}

Form.prototype.initEvent = function(events) {
    const keys = Object.getOwnPropertyNames(events);


    const keepSingleSpace = function(str) {
        var chars = str.split('');
        var hasSpace = false;
        var res = '';
        
        for(var i = 0, len = chars.length; i < len; i++) {
            if (chars[i] === ' ') {
                chars[i] = hasSpace ? '' : ' ';
                hasSpace = true;
            }
            res += chars[i];
        }
        return res;
    }

    keys.forEach(function(eventKey) {
        const eventKeyArr = keepSingleSpace(eventKey).split(' ');
        const selectorName = eventKeyArr[0]
        const eventName = eventKeyArr[1]
        $(selectorName).on(eventName, events[eventKey])
    })
}

Form.prototype.initSelect = function() {
    const selects = $(this.formElement).find('.dropdown');
    selects.each(function(i, el) {        
        const rootEl = $(el);
        const mapKey = rootEl.attr('id') || rootEl.find('.select_value').attr('name');
        this._selectMap[mapKey] = new Select(el);

    }.bind(this))
}

Form.prototype.getSelect = function(key) {
    return this._selectMap[key];
}

Form.prototype.initUpload = function() {
    const uploads = $(this.formElement).find('.upload-box')
    uploads.each(function(i, el) {
        const rootEl = $(el);
        rootEl.find('.upload-value').change(function() {
            const file = $(this).prop('files')[0]
            console.log(rootEl.find('.upload-text'))
            rootEl.find('.upload-text').val(file.name || '')
        })
    })
}



function Select(el) {
    this.$el = $(el)
    this.bindEvents('click', function(e) {
        const target = $(e.target)
        const curVal = target.data('val') || '';
        const curText = target.html() || '';
        this.setValue(curVal);
        if (curVal) {
            this.setText(curText)
        }
    }.bind(this));
}

Select.prototype.setOptions = function(datas) {
    if (!(datas instanceof Array)) {
        return;
    }

    const panel = this.$el.find('.dropdown-menu');

    const optionTempl = ['<li><a data-val="','">','</a></li>'];
    var optionListTempl = '';
    datas.forEach(function(data) {
        console.log(data)
        optionListTempl += optionTempl[0].concat(data.value, optionTempl[1], data.text, optionTempl[2]);
    }.bind(this))
    panel.html(optionListTempl);

}


Select.prototype.bindEvents = function(event ,cb) {
    this.$el.on(event, 'li a, li span', cb)
}

Select.prototype.setValue = function(value) {
    this.$el.find('.select_value').val(value);
    this.$el.find('.select_value').trigger('change');

    const setActiveProxy = this.setActive.bind(this);
    this.$el.find('li').each(function(i) {
        const curLi = $(this)
        if (curLi.children().eq(0).data('val') === value) {
            setActiveProxy(i)
        }
    })
}

Select.prototype.setText = function(text) {
    this.$el.find('.select_text').html(text);
}

Select.prototype.setActive = function(i) {
    this.$el.find('.active').removeClass('active');
    this.$el.find('li').eq(i).addClass('active');
}
