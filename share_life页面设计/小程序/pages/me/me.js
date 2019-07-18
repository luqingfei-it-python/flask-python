// pages/me/me.js

const app = getApp()
Page({

  /**
   * 页面的初始数据
   */
  data: {
    myinfo:null
  },
  history(){
    wx.navigateTo({
      url: '/pages/history/history',
    })
  },
  getData(){
    wx.navigateTo({
      url: '/pages/mydata/mydata',
    })
  },
  exit(){
    wx.request({
       url: 'http://192.168.43.110:5000/api/logout',
      type:'GET',
      success:function(res){
       //console.log(res)
        wx.navigateTo({
          url: '/pages/index/index',
        })
      }
    })
  },
  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    //=====》获取到当前登录的用户信息
    var that = this;
    wx.request({
       url: 'http://192.168.43.110:5000/api/public',
      type:'GET',
      success:function(res){
        console.log(res.data.data1)
        that.setData({
          myinfo:res.data.data1
        })
      }
    })
    //console.log("用户信息是" + app.globalData.userInfo);
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