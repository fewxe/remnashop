from typing import Sequence, Union

from alembic import op

revision: str = "0018"
down_revision: Union[str, None] = "0017"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TYPE payment_gateway_type ADD VALUE 'PLATEGA'
    """)


def downgrade() -> None:
    op.execute("""
        CREATE TYPE payment_gateway_type_backup AS ENUM (
            'TELEGRAM_STARS',
            'YOOKASSA',
            'YOOMONEY',
            'CRYPTOMUS',
            'HELEKET',
            'URLPAY'
        )
    """)
    op.execute("""
        ALTER TABLE payment_gateways ALTER COLUMN type 
        TYPE payment_gateway_type_backup 
        USING type::text::payment_gateway_type_backup
    """)
    op.execute("DROP TYPE payment_gateway_type")
    op.execute("ALTER TYPE payment_gateway_type_backup RENAME TO payment_gateway_type")
