import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters
from handlers.rps_game_handler import get_user_diamonds, update_diamonds, add_win_to_ranking, get_mention

ACTIVE_DICE_GAMES = {}

async def start_dice_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    user = update.effective_user
    
    if update.effective_chat.type == "private": return
    
    text = message.text
    import re
    match = re.match(r'^بازی\s+(\d+)$', text)
    if not match: return
    
    bet_amount = int(match.group(1))
    
    if bet_amount < 30:
        await message.reply_text("⚠️ حداقل شرط برای بازی ۳۰ طلا است!")
        return

    creator_diamonds = await get_user_diamonds(user.id)
    if creator_diamonds < bet_amount:
        await message.reply_text("❌ موجودی شما برای این شرط کافی نیست.")
        return

    # ۱. کسر مبلغ از سازنده بلافاصله هنگام ساخت بازی
    await update_diamonds(user.id, -bet_amount)

    game_id = f"dice_{user.id}_{message.message_id}"
    ACTIVE_DICE_GAMES[game_id] = {
        "creator_id": user.id,
        "creator_name": get_mention(user),
        "bet_amount": bet_amount,
        "status": "waiting"
    }

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("قبول", callback_data=f"dice_join_{game_id}"),
        InlineKeyboardButton("لغو", callback_data=f"dice_cancel_{game_id}")
    ]])
    
    await message.reply_text(
        f"<b>درخواست بازی {bet_amount}</b>\n\n"
        f"👤 سازنده: {get_mention(user)}\n"
        f"💰 شرط: {bet_amount} طلا\n\n"
        "💬 یک نفر برای شروع بازی باید دکمه <b>« قبول »</b> را بزند!",
        reply_markup=keyboard, parse_mode="HTML"
    )

async def handle_dice_clicks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user = query.from_user
    
    if data.startswith("dice_cancel_"):
        game_id = data.replace("dice_cancel_", "")
        game = ACTIVE_DICE_GAMES.get(game_id)
        
        if game and game["creator_id"] == user.id:
            # ۲. بازگرداندن طلا به سازنده در صورت لغو
            await update_diamonds(user.id, game["bet_amount"])
            del ACTIVE_DICE_GAMES[game_id]
            await query.edit_message_text("❌ بازی توسط سازنده لغو شد و طلا به حساب شما برگشت.")
        return

    if data.startswith("dice_join_"):
        game_id = data.replace("dice_join_", "")
        game = ACTIVE_DICE_GAMES.get(game_id)
        
        if not game or game["status"] != "waiting":
            await query.answer("❌ این بازی دیگر در دسترس نیست!", show_alert=True)
            return
            
        if user.id == game["creator_id"]:
            await query.answer("شما خودتان سازنده هستید!", show_alert=True)
            return

        bet = game["bet_amount"]
        opp_diamonds = await get_user_diamonds(user.id)
        
        if opp_diamonds < bet:
            await query.answer("موجودی شما کافی نیست!", show_alert=True)
            return

        # ۳. کسر مبلغ از نفر دوم
        await update_diamonds(user.id, -bet)
        game["status"] = "finished"

        # قرعه‌کشی (مساوی هم در نظر گرفته شد: عدد ۳)
        # ۱: برد سازنده، ۲: برد حریف، ۳: مساوی
        result = random.choice([1, 2, 3])
        
        if result == 3: # مساوی
            await update_diamonds(game["creator_id"], bet)
            await update_diamonds(user.id, bet)
            await query.edit_message_text("🤝 بازی مساوی شد! طلاها به هر دو نفر بازگشت.")
        else:
            winner = game["creator_id"] if result == 1 else user.id
            loser = user.id if result == 1 else game["creator_id"]
            
            # پرداخت جایزه به برنده (مجموع دو شرط)
            await update_diamonds(winner, 2 * bet)
            await add_win_to_ranking(winner, get_mention(winner))

            winner_balance = await get_user_diamonds(winner)
            loser_balance = await get_user_diamonds(loser)

            await query.edit_message_text(
                f"<b>بازی به پایان رسید!</b>\n\n"
                f"👑 برنده: {get_mention(winner)}\n"
                f"💰 موجودی برنده: {winner_balance}\n"
                f"💸 بازنده: {get_mention(loser)}\n"
                f"💰 موجودی بازنده: {loser_balance}", 
                parse_mode="HTML"
            )
        
        del ACTIVE_DICE_GAMES[game_id]

def register_dice_handlers(app):
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^بازی\s+(\d+)$'), start_dice_request))
    app.add_handler(CallbackQueryHandler(handle_dice_clicks, pattern=r'^dice_.*'))