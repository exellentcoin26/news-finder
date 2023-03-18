-- AlterTable
ALTER TABLE "NewsArticles" ALTER COLUMN "description" DROP NOT NULL,
ALTER COLUMN "photo" DROP NOT NULL,
ALTER COLUMN "publication_date" DROP NOT NULL;
