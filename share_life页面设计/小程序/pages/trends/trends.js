// pages/trends/trends.js
Page({

  /**
   * 页面的初始数据
   */
  data: {
    text:'',
    source:''
  },
  
  gettext(e) {
    this.setData({
      text: e.detail.value,
    })
  },
//上传图片

  upimg: function () {
    var that = this
    wx.chooseImage({ //从本地相册选择图片或使用相机拍照
      count: 1, // 默认9
      sizeType: ['original', 'compressed'], // 可以指定是原图还是压缩图，默认二者都有
      sourceType: ['album', 'camera'], // 可以指定来源是相册还是相机，默认二者都有
      success: function (res) {
        console.log(res)
        //前台显示
        that.setData({
          source: res.tempFilePaths
       })
      }
    })
  },

// //提交，发送数据
   submit:function(){
     var that = this
     wx.uploadFile({
        url: 'http://192.168.43.110:5000/api/create_dynamic',
       filePath: that.data.source[0],
       name: 'file',
       formData: {
         content: that.data.text
       },
       success: function (res) {
        // console.log(res.data)
         wx.switchTab({
           url:'/pages/home/home'
         })

//发表后清空
         that.setData({
           text:null,
           source:null
         })
       },
       error: function (res) {
         console.log(res)
       }
     })
       },
  

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {

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