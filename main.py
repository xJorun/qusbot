import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

app = Flask(__name__)
CORS(app)

authorized_user_id = 1146923509856096397

products_file = 'products.json'
past_work_file = 'past_work.json'

def setup_data_files():
    if not os.path.exists(products_file):
        with open(products_file, 'w') as f:
            json.dump([], f)
    
    if not os.path.exists(past_work_file):
        with open(past_work_file, 'w') as f:
            json.dump([], f)

def get_products():
    try:
        with open(products_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def get_past_work():
    try:
        with open(past_work_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def store_products(products):
    with open(products_file, 'w') as f:
        json.dump(products, f, indent=2)

def store_past_work(past_work):
    with open(past_work_file, 'w') as f:
        json.dump(past_work, f, indent=2)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    
    activity = discord.Activity(type=discord.ActivityType.watching, name="Managing Qustreso Studios content")
    await bot.change_presence(activity=activity, status=discord.Status.online)
    
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@bot.tree.command(name="add_product", description="Add a new product to the academy shop")
@app_commands.describe(
    name="The name of the product",
    link="The link to the product",
    video="The video URL for the product"
)
async def add_product(interaction: discord.Interaction, name: str, link: str, video: str):
    if interaction.user.id != authorized_user_id:
        await interaction.response.send_message("❌ You don't have permission to use this command!", ephemeral=True)
        return
    
    products = get_products()
    
    for product in products:
        if product['name'].lower() == name.lower():
            await interaction.response.send_message(f"❌ A product with the name '{name}' already exists!", ephemeral=True)
            return
    
    new_product = {
        'name': name,
        'link': link,
        'video': video,
        'added_by': interaction.user.name,
        'added_at': datetime.now().isoformat()
    }
    
    products.append(new_product)
    store_products(products)
    
    embed = discord.Embed(
        title="✅ Product Added Successfully",
        description=f"**{name}** has been added to the academy shop.",
        color=discord.Color.green()
    )
    embed.add_field(name="Link", value=link, inline=False)
    embed.add_field(name="Video", value=video, inline=False)
    embed.add_field(name="Added by", value=interaction.user.name, inline=True)
    embed.add_field(name="Added at", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="remove_product", description="Remove a product from the academy shop")
@app_commands.describe(name="The name of the product to remove")
async def remove_product(interaction: discord.Interaction, name: str):
    if interaction.user.id != authorized_user_id:
        await interaction.response.send_message("❌ You don't have permission to use this command!", ephemeral=True)
        return
    
    products = get_products()
    
    for i, product in enumerate(products):
        if product['name'].lower() == name.lower():
            removed_product = products.pop(i)
            store_products(products)
            
            embed = discord.Embed(
                title="✅ Product Removed Successfully",
                description=f"**{removed_product['name']}** has been removed from the academy shop.",
                color=discord.Color.red()
            )
            embed.add_field(name="Removed by", value=interaction.user.name, inline=True)
            embed.add_field(name="Removed at", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), inline=True)
            
            await interaction.response.send_message(embed=embed)
            return
    
    await interaction.response.send_message(f"❌ Product '{name}' not found!", ephemeral=True)

@bot.tree.command(name="list_products", description="List all products in the academy shop")
async def list_products(interaction: discord.Interaction):
    products = get_products()
    
    if not products:
        embed = discord.Embed(
            title="📦 Academy Shop Products",
            description="No products found in the shop.",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)
        return
    
    embed = discord.Embed(
        title="📦 Academy Shop Products",
        description=f"Found {len(products)} product(s):",
        color=discord.Color.blue()
    )
    
    for i, product in enumerate(products, 1):
        embed.add_field(
            name=f"{i}. {product['name']}",
            value=f"Link: {product['link']}\nVideo: {product['video']}\nAdded by: {product['added_by']}",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="add_past_work", description="Add a new past work project")
@app_commands.describe(
    name="The name of the past work project",
    video="The video URL for the past work"
)
async def add_past_work(interaction: discord.Interaction, name: str, video: str):
    if interaction.user.id != authorized_user_id:
        await interaction.response.send_message("❌ You don't have permission to use this command!", ephemeral=True)
        return
    
    past_work = get_past_work()
    
    for work in past_work:
        if work['name'].lower() == name.lower():
            await interaction.response.send_message(f"❌ A past work project with the name '{name}' already exists!", ephemeral=True)
            return
    
    new_work = {
        'name': name,
        'video': video,
        'added_by': interaction.user.name,
        'added_at': datetime.now().isoformat()
    }
    
    past_work.append(new_work)
    store_past_work(past_work)
    
    embed = discord.Embed(
        title="✅ Past Work Added Successfully",
        description=f"**{name}** has been added to past work.",
        color=discord.Color.green()
    )
    embed.add_field(name="Video", value=video, inline=False)
    embed.add_field(name="Added by", value=interaction.user.name, inline=True)
    embed.add_field(name="Added at", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="remove_past_work", description="Remove a past work project")
@app_commands.describe(name="The name of the past work project to remove")
async def remove_past_work(interaction: discord.Interaction, name: str):
    if interaction.user.id != authorized_user_id:
        await interaction.response.send_message("❌ You don't have permission to use this command!", ephemeral=True)
        return
    
    past_work = get_past_work()
    
    for i, work in enumerate(past_work):
        if work['name'].lower() == name.lower():
            removed_work = past_work.pop(i)
            store_past_work(past_work)
            
            embed = discord.Embed(
                title="✅ Past Work Removed Successfully",
                description=f"**{removed_work['name']}** has been removed from past work.",
                color=discord.Color.red()
            )
            embed.add_field(name="Removed by", value=interaction.user.name, inline=True)
            embed.add_field(name="Removed at", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), inline=True)
            
            await interaction.response.send_message(embed=embed)
            return
    
    await interaction.response.send_message(f"❌ Past work project '{name}' not found!", ephemeral=True)

@bot.tree.command(name="list_past_work", description="List all past work projects")
async def list_past_work(interaction: discord.Interaction):
    past_work = get_past_work()
    
    if not past_work:
        embed = discord.Embed(
            title="🎬 Past Work Projects",
            description="No past work projects found.",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)
        return
    
    embed = discord.Embed(
        title="🎬 Past Work Projects",
        description=f"Found {len(past_work)} project(s):",
        color=discord.Color.blue()
    )
    
    for i, work in enumerate(past_work, 1):
        embed.add_field(
            name=f"{i}. {work['name']}",
            value=f"Video: {work['video']}\nAdded by: {work['added_by']}",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"⏰ This command is on cooldown. Try again in {error.retry_after:.2f} seconds.", ephemeral=True)
    elif isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ You don't have the required permissions to use this command!", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ An error occurred: {str(error)}", ephemeral=True)

@app.route('/')
def home():
    return jsonify({
        "message": "Qustreso Studios API",
        "version": "1.0.0",
        "endpoints": {
            "products": "/api/products",
            "past_work": "/api/past-work",
            "stats": "/api/stats"
        }
    })

@app.route('/api/products')
def get_products_api():
    products = get_products()
    return jsonify({
        "success": True,
        "count": len(products),
        "products": products
    })

@app.route('/api/products/<product_name>')
def get_product_api(product_name):
    products = get_products()
    
    for product in products:
        if product['name'].lower() == product_name.lower():
            return jsonify({
                "success": True,
                "product": product
            })
    
    return jsonify({
        "success": False,
        "error": "Product not found"
    }), 404

@app.route('/api/past-work')
def get_past_work_api():
    past_work = get_past_work()
    return jsonify({
        "success": True,
        "count": len(past_work),
        "past_work": past_work
    })

@app.route('/api/past-work/<work_name>')
def get_past_work_item_api(work_name):
    past_work = get_past_work()
    
    for work in past_work:
        if work['name'].lower() == work_name.lower():
            return jsonify({
                "success": True,
                "past_work": work
            })
    
    return jsonify({
        "success": False,
        "error": "Past work project not found"
    }), 404

@app.route('/api/stats')
def get_stats_api():
    products = get_products()
    past_work = get_past_work()
    
    return jsonify({
        "success": True,
        "stats": {
            "total_products": len(products),
            "total_past_work": len(past_work),
            "last_updated": datetime.now().isoformat()
        }
    })

@app.route('/api/search')
def search_api():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({
            "success": False,
            "error": "Search query required"
        }), 400
    
    products = get_products()
    past_work = get_past_work()
    
    matching_products = [
        product for product in products 
        if query in product['name'].lower()
    ]
    
    matching_past_work = [
        work for work in past_work 
        if query in work['name'].lower()
    ]
    
    return jsonify({
        "success": True,
        "query": query,
        "results": {
            "products": matching_products,
            "past_work": matching_past_work
        },
        "counts": {
            "products": len(matching_products),
            "past_work": len(matching_past_work)
        }
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500

def start_api_server():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    setup_data_files()
    
    bot_token = "MTM5NTc2MzAyOTkyMDA1OTUzNg.G76qmf.dHwSV57vYlTDi5sgq1z4AZLq7SGXXOG8ikcqwo"
    
    if bot_token == "YOUR_BOT_TOKEN_HERE":
        print("❌ Please replace 'YOUR_BOT_TOKEN_HERE' with your actual Discord bot token!")
        exit(1)
    
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Starting API server on port {port}...")
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    
    print("🤖 Starting Discord bot...")
    print(f"📡 API will be available at: http://localhost:{port}")
    print("📋 Available API endpoints:")
    print("   - GET /api/products")
    print("   - GET /api/past-work")
    print("   - GET /api/stats")
    print("   - GET /api/search?q=<query>")
    
    bot.run(bot_token) 
