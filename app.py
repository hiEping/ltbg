# 导入必要的库
from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import hashlib
import json
import logging
from logging.handlers import TimedRotatingFileHandler
import os

# 初始化应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'lyjt1204'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market_monitor.db?charset=utf-8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # 初始化 Migrate

# 全局配置变量
API_CONFIG = {}

# ======================================
# 数据库模型定义
# ======================================

# 用户表
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    # 联系电话
    telephone = db.Column(db.String(20))

# 3.4 市场监测日度农贸价格数据
class MmsPriceRpt(db.Model):
    __tablename__ = 'mms_price_rpt'
    # 企业统一平台编码
    loginName = db.Column(db.String(50), nullable=False)
    # 品类编码
    commodityId = db.Column(db.String(20), primary_key=True)
    # 零售价格
    price = db.Column(db.Float, nullable=False)
    # 报表日期，格式为“yyyy-MM-dd”
    rptdate = db.Column(db.Date, primary_key=True, default=datetime.now)
    # 报送日期，格式为“yyyy-MM-dd hh24:mi:ss”
    createTime = db.Column(db.DateTime, nullable=False, default=datetime.now)
    # 修改时间，格式为“yyyy-MM-dd hh24:mi:ss”
    updateTime = db.Column(db.DateTime, nullable=False, default=datetime.now)
    # 联系人
    linkman = db.Column(db.String(50), nullable=False)
    # 联系电话
    telephone = db.Column(db.String(20), nullable=False)
    # 简要分析
    memo = db.Column(db.String(200), nullable=False, default='正常波动')
    # 单位负责人
    leader = db.Column(db.String(50), nullable=False)
    # 统计负责人
    statistician = db.Column(db.String(50), nullable=False)

# 3.6 应急保供日度批发进销存数据
class WisDayJxcRpt(db.Model):
    __tablename__ = 'wis_day_jxc_rpt'
    # 企业统一平台编码
    loginName = db.Column(db.String(50), primary_key=True)
    # 品类编码
    commodityId = db.Column(db.String(20), primary_key=True)
    # 交易量
    amount = db.Column(db.Float, nullable=False)
    # 库存量
    stock = db.Column(db.Float, nullable=False)
    # 进货量
    instock = db.Column(db.Float, nullable=False)
    # 报表日期，格式为“yyyy-MM-dd”
    rptdate = db.Column(db.Date, primary_key=True, default=datetime.now)
    # 报送日期，格式为“yyyy-MM-dd hh24:mi:ss”
    createTime = db.Column(db.DateTime, nullable=False, default=datetime.now)
    # 修改时间，格式为“yyyy-MM-dd hh24:mi:ss”
    updateTime = db.Column(db.DateTime, nullable=False, default=datetime.now)
    # 联系人
    linkman = db.Column(db.String(50), nullable=False)
    # 联系电话
    telephone = db.Column(db.String(20), nullable=False)
    # 简要分析
    memo = db.Column(db.String(200), nullable=False, default='正常波动')
    # 单位负责人
    leader = db.Column(db.String(50), nullable=False)
    # 统计负责人
    statistician = db.Column(db.String(50), nullable=False)
    # 产地，传6位地区编码。
    originPlace = db.Column(db.String(6), primary_key=True)
    # 生产商名称
    manufacturerName = db.Column(db.String(150), nullable=False)
    # 生产商地址
    manufacturerAddress = db.Column(db.String(250), nullable=False)

# 3.10 重点零售企业商品销售额统计旬报
class ODS_ZDLSQY_SBXSE_XB(db.Model):
    __tablename__ = str.lower('ODS_ZDLSQY_SBXSE_XB')
    # 统一社会信用代码
    TYSHXYDM = db.Column(db.String(40), primary_key=True)
    # 单位详细名称
    DWMC = db.Column(db.String(40), nullable=False)
    # 报表期，格式为“YYYYMM上旬”“YYYYMM中旬”“YYYYMM下旬”
    BBQ = db.Column(db.String(12), primary_key=True)
    # 单位负责人
    DWFZR = db.Column(db.String(50), nullable=False)
    # 填表人
    TBR = db.Column(db.String(50), nullable=False)
    # 联系电话
    LXDH = db.Column(db.String(20), nullable=False)
    # 报表日期，格式为“yyyy-MM-dd”
    BCRQ = db.Column(db.Date, nullable=False, default=datetime.now)
    # 指标
    ZB = db.Column(db.String(8), primary_key=True)
    # 本期值
    BQZ = db.Column(db.Float)
    # 去年同期值
    QNTQZ = db.Column(db.Float)
    
# 3.12 （网点维度）应急保供日度批发进销存数据信息
class WisUploadProductDtl(db.Model):
    __tablename__ = str.lower('Wis_Upload_Product_Dtl')
    # 网点编码(网点唯一编码)网点编码和网点外部编码不能同时为空
    nodeCode = db.Column(db.String(20), default='')
    # 网点外部编码（企业维护唯一编码）网点编码和网点外部编码不能同时为空
    foreignId = db.Column(db.String(20), primary_key=True)
    # 品类编码，详见附录：应急保供零售品类字典表
    commodityId = db.Column(db.String(20), primary_key=True)
    # 库存量
    stock = db.Column(db.Float, nullable=False)
    # 进货量
    instock = db.Column(db.Float, nullable=False)
    # 销售量
    amount = db.Column(db.Float, nullable=False)
    # 报表时间yyyy-MM-dd hh:mm:ss
    rptdate = db.Column(db.Date, primary_key=True, default=datetime.now)

# 市场监测品类字典表（码表4.1）
class ScjcPl(db.Model):
    __tablename__ = 'scjc_pl_dict'
    commodity_id = db.Column(db.String(20), primary_key=True)
    commodity_name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.String(20))
    type = db.Column(db.String(20))
    price_unit = db.Column(db.String(20))
    unit = db.Column(db.String(20))

# 应急保供零售品类字典表（码表4.2）
class YjbgLsPl(db.Model):
    __tablename__ = 'yjbg_ls_pl_dict'
    commodity_id = db.Column(db.String(20), primary_key=True)
    commodity_name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.String(20))
    unit = db.Column(db.String(20))

# 应急保供批发品类字典表（码表4.3）
class YjbgPfPl(db.Model):
    __tablename__ = 'yjbg_pf_pl_dict'
    commodity_id = db.Column(db.String(20), primary_key=True)
    commodity_name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.String(20))
    unit = db.Column(db.String(20))

# 重点零售企业销售情况旬报字典表（码表4.5）
class XbZb(db.Model):
    __tablename__ = 'xb_zb_dict'
    zb_id = db.Column(db.String(20), primary_key=True)
    zb_name = db.Column(db.String(100), nullable=False)
    zb_unit = db.Column(db.String(20))

# 区域名称代码字典表（码表4.7与4.8）
class QyCode(db.Model):
    __tablename__ = 'qy_code_dict'
    qy_code = db.Column(db.String(20), primary_key=True)
    qy_name = db.Column(db.String(100), nullable=False)

# 价格类型字典表（码表3）
class PriceTypeDict(db.Model):
    __tablename__ = 'price_type_dict'
    price_type_id = db.Column(db.String(20), primary_key=True)
    price_type_name = db.Column(db.String(100), nullable=False)

# ======================================
# 日志配置
# ======================================
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

# 登录日志
login_handler = TimedRotatingFileHandler(
    os.path.join(log_dir, 'login.log'),
    when='midnight',
    backupCount=30
)

# 表单操作日志
form_handler = TimedRotatingFileHandler(
    os.path.join(log_dir, 'form_ops.log'),
    when='midnight',
    backupCount=30
)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
login_handler.setFormatter(formatter)
form_handler.setFormatter(formatter)

app.logger.addHandler(login_handler)
app.logger.addHandler(form_handler)
app.logger.setLevel(logging.INFO)

# ======================================
# 工具函数
# ======================================
def encrypt_password(password):
    """密码加密函数"""
    return hashlib.sha256(password.encode()).hexdigest()

def save_log(log_type, message):
    """保存日志"""
    logger = app.logger
    if log_type == 'login':
        logger.info(f'登录日志: {message}')
    elif log_type == 'form':
        logger.info(f'表单操作: {message}')

# ======================================
# 路由定义
# ======================================

# 登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == encrypt_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['telephone'] = user.telephone
            save_log('login', f'用户{username}登录成功')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误', 'error')
    
    return render_template('login.html')


# 登出
@app.route('/logout')
def logout():
    username = session.get('username', '未知用户')
    session.pop('user_id', None)
    session.pop('username', None)
    save_log('login', f'{username}用户登出')
    return redirect(url_for('login'))

# 默认页
@app.route('/')
@app.route('/index')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

# 仪表盘
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 统计数据
    retail_count = MmsPriceRpt.query.count()
    wholesale_count = WisDayJxcRpt.query.count()
    user_count = User.query.count()
    
    return render_template('dashboard.html', 
                          retail_count=retail_count,
                          wholesale_count=wholesale_count,
                          user_count=user_count)

# 市场监测日度农贸价格数据
@app.route('/retail_prices', methods=['GET', 'POST'])
def retail_prices():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 获取当前用户
    username = session.get('username')    
    telephone = session.get('telephone')
    today = datetime.today().strftime('%Y-%m-%d')

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            # 添加新记录
            commodity_id = request.form.get('commodity_id')
            price = request.form.get('price')
            rptdate = request.form.get('rptdate')
            
            try:
                price = float(price)
                new_record = MmsPriceRpt(
                    login_name=username,
                    commodity_id=commodity_id,
                    price=price,
                    rptdate=rptdate
                )
                db.session.add(new_record)
                db.session.commit()
                flash('添加成功', 'success')
                save_log('form', f'用户{username}添加零售价格记录，商品ID:{commodity_id}')
            except Exception as e:
                db.session.rollback()
                flash(f'添加失败: {str(e)}', 'error')
        
        elif action == 'edit':
            # 编辑记录
            record_id = request.form.get('record_id')
            commodity_id = request.form.get('commodity_id')
            price = request.form.get('price')
            rptdate = request.form.get('rptdate')
            
            try:
                record = MmsPriceRpt.query.get(record_id)
                if record:
                    record.commodity_id = commodity_id
                    record.price = float(price)
                    record.rptdate = rptdate
                    record.update_time = datetime.now()
                    db.session.commit()
                    flash('更新成功', 'success')
                    save_log('form', f'用户{username}更新零售价格记录，ID:{record_id}')
                else:
                    flash('记录不存在', 'error')
            except Exception as e:
                db.session.rollback()
                flash(f'更新失败: {str(e)}', 'error')
        
        elif action == 'delete':
            # 删除记录
            record_id = request.form.get('record_id')
            try:
                record = MmsPriceRpt.query.get(record_id)
                if record:
                    db.session.delete(record)
                    db.session.commit()
                    flash('删除成功', 'success')
                    save_log('form', f'用户{username}删除零售价格记录，ID:{record_id}')
                else:
                    flash('记录不存在', 'error')
            except Exception as e:
                db.session.rollback()
                flash(f'删除失败: {str(e)}', 'error')
        
    # 获取商品字典
    # commodities = ScjcPl.query.all()
    # commodity_map = {c.commodity_id: c.commodity_name for c in commodities}
    
    return render_template('retail_prices.html', 
                        #   data=data, 
                        #   pagination=pagination,
                            username=username,
                            today=today,
                            telephone=telephone,
                            # commodities=commodities,
                            # commodity_map=commodity_map
                            )

# 应急保供日度批发进销存数据
@app.route('/pfJxc', methods=['GET', 'POST'])
def emergency_wholesale():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 获取当前用户
    username = session.get('username')
    
    return render_template('pfJxc.html', 
                        #   data=data, 
                        #   pagination=pagination,
                        #   commodities=commodities,
                        #   commodity_map=commodity_map
                          )

# 重点零售企业商品销售额统计旬报
@app.route('/zb_xb', methods=['GET', 'POST'])
def zb_xb():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 获取当前用户
    username = session.get('username')

    return render_template("zb_xb.html")

# （网点维度）应急保供日度批发进销存数据信息
@app.route('/wdPfJxc', methods=['GET', 'POST'])
def wdDaily():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 获取当前用户
    username = session.get('username')

    return render_template('wdPfJxc.html')

# 用户管理页面
@app.route('/user_management', methods=['GET', 'POST'])
def user_management():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 仅允许特定用户访问（如管理员）
    # 此处简化处理，实际应用中应实现更完善的权限管理
    if session.get('username') != 'admin':
        flash('无权限访问', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            # 添加用户
            login_name = request.form.get('login_name')
            password = request.form.get('password')
            linkman = request.form.get('linkman')
            telephone = request.form.get('telephone')
            
            try:
                # 检查用户名是否已存在
                if User.query.filter_by(login_name=login_name).first():
                    flash('用户名已存在', 'error')
                    return redirect(url_for('user_management'))
                
                new_user = User(
                    login_name=login_name,
                    password=encrypt_password(password),
                    linkman=linkman,
                    telephone=telephone
                )
                db.session.add(new_user)
                db.session.commit()
                flash('用户添加成功', 'success')
                save_log('form', f'管理员添加用户: {login_name}')
            except Exception as e:
                db.session.rollback()
                flash(f'用户添加失败: {str(e)}', 'error')
        
        elif action == 'edit':
            # 编辑用户
            user_id = request.form.get('user_id')
            linkman = request.form.get('linkman')
            telephone = request.form.get('telephone')
            
            try:
                user = User.query.get(user_id)
                if user:
                    user.linkman = linkman
                    user.telephone = telephone
                    db.session.commit()
                    flash('用户信息更新成功', 'success')
                    save_log('form', f'管理员更新用户信息，ID:{user_id}')
                else:
                    flash('用户不存在', 'error')
            except Exception as e:
                db.session.rollback()
                flash(f'用户信息更新失败: {str(e)}', 'error')
        
        elif action == 'change_password':
            # 修改密码
            user_id = request.form.get('user_id')
            new_password = request.form.get('new_password')
            
            try:
                user = User.query.get(user_id)
                if user:
                    user.password = encrypt_password(new_password)
                    db.session.commit()
                    flash('密码修改成功', 'success')
                    save_log('form', f'管理员修改用户密码，ID:{user_id}')
                else:
                    flash('用户不存在', 'error')
            except Exception as e:
                db.session.rollback()
                flash(f'密码修改失败: {str(e)}', 'error')
        
        elif action == 'delete':
            # 删除用户
            user_id = request.form.get('user_id')
            
            try:
                user = User.query.get(user_id)
                if user:
                    # 不能删除自己
                    if int(user_id) == session.get('user_id'):
                        flash('不能删除当前登录用户', 'error')
                        return redirect(url_for('user_management'))
                    
                    db.session.delete(user)
                    db.session.commit()
                    flash('用户删除成功', 'success')
                    save_log('form', f'管理员删除用户，ID:{user_id}')
                else:
                    flash('用户不存在', 'error')
            except Exception as e:
                db.session.rollback()
                flash(f'用户删除失败: {str(e)}', 'error')
    
    # 查询用户数据
    users = User.query.all()
    return render_template('user_management.html', users=users)

def get_project_root():
    """获取项目根目录路径"""
    # 假设app.py位于项目根目录或其子目录中
    current_file = os.path.abspath(__file__)
    return os.path.dirname(current_file)

def load_config():
    """加载配置文件内容到全局变量"""
    global API_CONFIG
    project_root = get_project_root()
    # 配置文件位于static目录下
    config_path = os.path.join(project_root, 'static', 'settings.json')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            API_CONFIG = json.load(f)
        print(f"配置文件加载成功: {config_path}")
    except FileNotFoundError:
        print(f"错误: 配置文件 {config_path} 不存在")
        API_CONFIG = {
            "api1": "http://default-api1.com",
            "api2": "http://default-api2.com",
            "api3": "http://default-api3.com",
            "api4": "http://default-api4.com"
        }
    except json.JSONDecodeError:
        print(f"错误: 配置文件 {config_path} 格式不正确")
        API_CONFIG = {}

# 项目启动时加载配置
load_config()

if __name__ == '__main__':
    app.run(debug=True)    