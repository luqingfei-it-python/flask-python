// pages/home/home.js
Page({

  /**
   * 页面的初始数据
   */
  data: {
    list:null,
    data1:'',
    user_history:'',
    dynamic_id:'',
    dynamic_c:'',
    showView: false,
    comment:'',
    dynamic_d:''
  },
  getdetail(e){
    this.setData({
      dynamic_d: e.currentTarget.dataset.id
    })
    wx.request({
       url: 'http://192.168.43.110:5000/api/detail',
      method: 'GET',
      data:{
        dynamic_id:this.data.dynamic_d
      },
      success: function (res) {
        console.log(res)
        wx.navigateTo({
          url: '../detail/detail?data=' + JSON.stringify(res.data)
        })
      }
    })
  },

  //点赞图标的变化
  iconClick: function (e) {
    //当前点击的dynamic_id，根据dynamic_id找到对应用户信息
    this.setData({
      dynamic_id: e.currentTarget.dataset.id
    }) 
    wx.request({
       url: 'http://192.168.43.110:5000/api/goods',
      type:'GET',
      data: {
        dynamic_id: this.data.dynamic_id
      },
      success: function(res) {
        console.log(res)
      },
      fail: function(res) {
        console.log(res)
      },
    })

    //判断赞的点击状态
    var index = e.currentTarget.dataset.index;
    var that = this;
    for (var i in this.data.list) {
      //判断条件，当前点击就点赞
      if (index == i) {
          that.setData({
            ['list[' + i + '].status']: 'true',
          })
          wx.showToast({
            title: '点赞加1',
            icon: 'success',
            duration: 500
          })
        }
      }
  },

  // 评论功能
  //判断评论图标变化，弹出评论框
  onChangeShowState: function (e) {
    //用户评论的id
    this.setData({
      dynamic_c: e.currentTarget.dataset.id
    })

    //用户对应的评论框
    var index = e.currentTarget.dataset.index;
    var that = this;
    for(var i in that.data.list){
      if(index == i){
        that.setData({
        showView: (!that.data.showView)
        })
      }
    }
  
  },
  // 获取评论框信息
  getcoment(e){
      this.setData({
        comment:e.detail.value
      })
  },
  
  getCommit(e){
//发送id和评论内容
    var that = this;
    wx.request({
       url: 'http://192.168.43.110:5000/api/dynamic_comment',
      method: 'POST',
      header: {
        'content-type': "application/x-www-form-urlencoded"
      },
      data: {
        dynamic_id: this.data.dynamic_c,
        comment:this.data.comment
      },
      success: function (res) {
        console.log(res)
        wx.showToast({
          title: '评论成功',
          icon: 'success',
          duration: 2000
        })
        that.setData({
          showView: (!that.data.showView),
          comment:null
        })
      },
      fail: function (res) {
        console.log(res)
      },
    })
  },

  // 点击用户头像到更圈历史页面
  user_history(e){
    this.setData({
      user_history:e.currentTarget.dataset.id
    })
    wx:wx.request({
       url: 'http://192.168.43.110:5000/api/get_other',
      data: {
        other_id:this.data.user_history
      },
      method: 'GET',
      success: function(res) {
        wx.navigateTo({
          url: '/pages/user_history/user_history?data=' + JSON.stringify(res.data),
        })
      }
    })
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    //showView: (options.showView == "true" ? false : true)
  },
  

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady: function () {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () {
    var that = this;
    wx.request({
       url: 'http://192.168.43.110:5000/api/public',
      type: 'GET',
      success: function (res) {
        console.log(res)
        that.setData({
          list: res.data.data
        })
      }
    })
  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide: function () {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload: function () {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh: function () {

  },
  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom: function () {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage: function () {

  }
})