from aiogram import Router, types
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent
from sqlalchemy import select
from ..database import async_session_maker
from ..models import FAQ

router = Router()


@router.inline_query()
async def inline_faq(inline_query: types.InlineQuery):
    query = inline_query.query.strip()
    async with async_session_maker() as session:
        if query:
            results = await session.execute(
                select(FAQ)
                .where(FAQ.question.ilike(f"%{query}%"), FAQ.is_active == True)
                .order_by(FAQ.order)
            )
        else:
            results = await session.execute(
                select(FAQ).where(FAQ.is_active == True).order_by(FAQ.order).limit(10)
            )
        faqs = results.scalars().all()

    articles = []
    for faq in faqs:
        articles.append(
            InlineQueryResultArticle(
                id=str(faq.id),
                title=faq.question[:100],
                description=faq.answer[:150],
                input_message_content=InputTextMessageContent(
                    message_text=f"<b>{faq.question}</b>\n\n{faq.answer}"
                ),
            )
        )
    await inline_query.answer(articles, cache_time=10)
