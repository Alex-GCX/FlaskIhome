
function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

function updateFilterDateDisplay() {
    var startDate = $("#start-date").val();
    var endDate = $("#end-date").val();
    var $filterDateTitle = $(".filter-title-bar>.filter-title").eq(0).children("span").eq(0);
    if (startDate) {
        var text = startDate.substr(5) + "/" + endDate.substr(5);
        $filterDateTitle.html(text);
    } else {
        $filterDateTitle.html("入住日期");
    }
}


function send_ajax(areaId, startDate, endDate, page, sortedBy){
    //处理参数
    if (areaId == undefined){
        areaId = ''
    }
    if (startDate == undefined){
        startDate = ''
    }
    if (endDate == undefined){
        endDate = ''
    }
    if (page == undefined){
        page = 1
    }
    if (sortedBy == undefined){
        sortedBy = 'latest'
    }
    //发送ajax请求执行查询
    var searchUrl ='api/v1.0/search/houses?aid='+areaId+'&sd='+startDate+'&ed='+endDate+'&page='+page+'&sorted_by='+sortedBy;
    $.get(searchUrl, function (resp) {
        if (resp.errno == '0'){
            //查询成功
            //使用模板设置查询结果
            $('.house-list').html(template('search-houses', {houses: resp.data}));
        }else{
            //查询失败
            alert(resp.errmsg);
        }
    }, 'json');
}


$(document).ready(function(){
    //获取url查询条件
    var queryData = decodeQuery();
    //提取查询条件
    var areaId = queryData["aid"];
    var areaName = queryData["aname"];
    var startDate = queryData["sd"];
    var endDate = queryData["ed"];
    var page = queryData["page"];
    var sortedBy = queryData["sorted_by"];
    //将url的查询日期设置到日期查询框中
    $("#start-date").val(startDate); 
    $("#end-date").val(endDate); 
    updateFilterDateDisplay();
    //url中不存在地区条件地区选择框显示'位置区域'
    if (!areaName) areaName = "位置区域";
    $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).html(areaName);

    //发送ajax请求查询地区信息
    $.get('api/v1.0/areas', function (resp) {
        if (resp.errno == '0'){
            //获取成功
            $('.filter-area').html(template('search-areas', {areas: resp.data}));
        }
    }, 'json');

    // 发送查询请求
    send_ajax(areaId, startDate, endDate, page, sortedBy);

    $(".input-daterange").datepicker({
        format: "yyyy-mm-dd",
        startDate: "today",
        language: "zh-CN",
        autoclose: true
    });

    //统一管理查询条件选择框
    var $filterItem = $(".filter-item-bar>.filter-item");
    $(".filter-title-bar").on("click", ".filter-title", function(e){
        var index = $(this).index();
        if (!$filterItem.eq(index).hasClass("active")) {
            $(this).children("span").children("i").removeClass("fa-angle-down").addClass("fa-angle-up");
            $(this).siblings(".filter-title").children("span").children("i").removeClass("fa-angle-up").addClass("fa-angle-down");
            $filterItem.eq(index).addClass("active").siblings(".filter-item").removeClass("active");
            $(".display-mask").show();
        } else {
            $(this).children("span").children("i").removeClass("fa-angle-up").addClass("fa-angle-down");
            $filterItem.eq(index).removeClass('active');
            $(".display-mask").hide();
            updateFilterDateDisplay();
        }
    });

    //地区选择框的点击事件
    $(".filter-item-bar>.filter-area").on("click", "li", function(e) {
        if (!$(this).hasClass("active")) {
            $(this).addClass("active");
            $(this).siblings("li").removeClass("active");
            $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).html($(this).html());
        } else {
            $(this).removeClass("active");
            $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).html("位置区域");
        }
        //点击后隐藏选择框
        $('.filter-area').removeClass("active");
        $(".display-mask").click();
    });

    //排序选择框的点击事件
    $(".filter-item-bar>.filter-sort").on("click", "li", function(e) {
        if (!$(this).hasClass("active")) {
            $(this).addClass("active");
            $(this).siblings("li").removeClass("active");
            $(".filter-title-bar>.filter-title").eq(2).children("span").eq(0).html($(this).html());
            //点击后隐藏选择框
            $('.filter-sort').removeClass("active");
            $(".display-mask").click();
        }
    })

    //查询条件底部灰框的点击事件
    $(".display-mask").on("click", function(e) {
        $(this).hide();
        $filterItem.removeClass('active');
        updateFilterDateDisplay();
        // 发送查询请求
        var areaId = $('.filter-area li[class="active"]').attr('area-id')
        var startDate = $("#start-date").val();
        var endDate = $("#end-date").val();
        send_ajax(areaId, startDate, endDate, page, sortedBy);
    });
})