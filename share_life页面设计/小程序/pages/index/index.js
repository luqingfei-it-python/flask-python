//index.js
//获取应用实例
const app = getApp()

Page({
  data: {
    motto: 'Hello World',
    userInfo: {},
    hasUserInfo: false,
    canIUse: wx.canIUse('button.open-type.getUserInfo')
  },
  //事件处理函数
  bindViewTap: function() {
    wx.navigateTo({
      url: '../logs/logs'
    })
  },
  //添加的index跳转到home页面
  getHome: function (event) {
    wx.switchTab({
      url: '../home/home',
    })
  },
  onLoad: function () {
  
  },
  getUserInfo: function(e) {
    app.globalData.userInfo = e.detail.userInfo
    this.setData({
      userInfo: e.detail.userInfo,
      hasUserInfo: true
    })
    wx.request({
       url: 'http://192.168.43.110:5000/api/get_userinfo',
      method:"POST",
      header:{
        'content-type':"application/x-www-form-urlencoded"
      },
      data:{
        code: app.globalData.codes,
        userinfo: JSON.stringify(this.data.userInfo),
       // encryptedData: app.globalData.encryptedData,
       // iv: app.globalData.iv
      },
      success:function(res){
        console.log(res);
      },
    })
   // console.log(this.data.userInfo)
  },

})
